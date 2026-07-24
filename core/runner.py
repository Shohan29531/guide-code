from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ALLOWED_IMPORTS = {"bisect", "collections", "functools", "heapq", "itertools", "math"}
BLOCKED_CALLS = {
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "globals",
    "input",
    "locals",
    "open",
    "vars",
    "__import__",
}
BLOCKED_ATTRIBUTES = {
    "system",
    "popen",
    "spawn",
    "fork",
    "remove",
    "unlink",
    "rmdir",
    "chmod",
    "chown",
    "kill",
    "terminate",
    "connect",
    "listen",
    "accept",
    "send",
    "recv",
}


def validate_code(code: str) -> list[str]:
    """Apply lightweight safety checks before running learner code locally."""
    errors: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"Syntax error on line {exc.lineno}: {exc.msg}"]

    solve_found = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "solve":
            solve_found = True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    errors.append(f"Import `{root}` is not allowed in the local runner.")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                errors.append(f"Import from `{root or 'relative module'}` is not allowed.")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                errors.append(f"Call to `{node.func.id}` is not allowed.")
            if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_ATTRIBUTES:
                errors.append(f"Call to attribute `{node.func.attr}` is not allowed.")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            errors.append("Dunder attribute access is not allowed.")

    if not solve_found:
        errors.append("Define the required `solve` function.")
    return list(dict.fromkeys(errors))


def _run_python_tests(
    code: str,
    tests: list[dict[str, Any]],
    timeout_seconds: int = 3,
) -> dict[str, Any]:
    validation_errors = validate_code(code)
    if validation_errors:
        return {
            "status": "validation_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": "\n".join(validation_errors),
            "stdout": "",
        }

    runner_source = f'''\
import copy
import json
import traceback

try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    # 256 MB address-space limit where supported.
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
except Exception:
    pass

USER_CODE = {code!r}
TESTS = {tests!r}
namespace = {{}}
payload = {{"status": "completed", "passed": 0, "total": len(TESTS), "results": [], "error": ""}}

def freeze(value):
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    if isinstance(value, dict):
        return tuple(sorted((key, freeze(item)) for key, item in value.items()))
    return value

def values_match(actual, expected, comparison):
    if comparison == "float":
        try:
            return abs(float(actual) - float(expected)) <= 1e-5
        except (TypeError, ValueError):
            return False
    if comparison == "unordered_nested":
        if not isinstance(actual, list) or not isinstance(expected, list):
            return False
        return sorted(map(repr, map(freeze, actual))) == sorted(
            map(repr, map(freeze, expected))
        )
    return actual == expected

try:
    exec(compile(USER_CODE, "<learner_code>", "exec"), namespace, namespace)
    solve = namespace.get("solve")
    if not callable(solve):
        raise TypeError("`solve` is not callable")

    for index, test in enumerate(TESTS, start=1):
        args = copy.deepcopy(test["args"])
        expected = copy.deepcopy(test["expected"])
        try:
            actual = solve(*args)
            passed = values_match(actual, expected, test.get("comparison", "exact"))
            if passed:
                payload["passed"] += 1
            payload["results"].append({{
                "test": index,
                "passed": passed,
                "input": test["args"],
                "expected": expected,
                "actual": actual,
                "error": "",
            }})
        except Exception:
            payload["results"].append({{
                "test": index,
                "passed": False,
                "input": test["args"],
                "expected": expected,
                "actual": None,
                "error": traceback.format_exc(limit=4),
            }})
except Exception:
    payload["status"] = "runtime_error"
    payload["error"] = traceback.format_exc(limit=6)

print("__GUIDED_CODE_RESULT__" + json.dumps(payload, default=repr))
'''

    with tempfile.TemporaryDirectory(prefix="guided_code_") as temp_dir:
        runner_path = Path(temp_dir) / "runner.py"
        runner_path.write_text(runner_source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(runner_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "timeout",
                "passed": 0,
                "total": len(tests),
                "results": [],
                "error": f"Execution exceeded {timeout_seconds} seconds.",
                "stdout": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
            }

    stdout = completed.stdout or ""
    marker = "__GUIDED_CODE_RESULT__"
    marker_index = stdout.rfind(marker)
    if marker_index == -1:
        return {
            "status": "runner_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": (completed.stderr or "Runner did not return a valid result.")[-4000:],
            "stdout": stdout[-3000:],
        }

    learner_stdout = stdout[:marker_index].strip()
    raw_payload = stdout[marker_index + len(marker):].strip().splitlines()[0]
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return {
            "status": "runner_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": "Runner returned malformed output.",
            "stdout": stdout[-3000:],
        }

    payload["stdout"] = learner_stdout[-3000:]
    if completed.returncode != 0 and payload.get("status") == "completed":
        payload["status"] = "runner_error"
        payload["error"] = (completed.stderr or "Process exited unexpectedly.")[-4000:]
    return payload


JAVASCRIPT_BLOCKED_PATTERNS = (
    (r"\brequire\s*\(", "`require` is not allowed in the local runner."),
    (r"\bimport\b", "Imports are not allowed in the local runner."),
    (r"\bprocess\b", "`process` access is not allowed in the local runner."),
    (r"\bfetch\s*\(", "Network requests are not allowed in the local runner."),
    (r"\bWebSocket\b", "Network access is not allowed in the local runner."),
    (r"\b(?:Deno|Bun)\b", "Runtime APIs are not allowed in the local runner."),
    (r"\beval\s*\(", "`eval` is not allowed in the local runner."),
    (r"\bFunction\s*\(", "Dynamic function creation is not allowed in the local runner."),
    (r"\bconstructor\b", "Constructor-chain access is not allowed in the local runner."),
)


def validate_javascript_code(code: str) -> list[str]:
    errors: list[str] = []
    solve_pattern = (
        r"\bfunction\s+solve\s*\("
        r"|\b(?:const|let|var)\s+solve\s*="
        r"|\bsolve\s*=\s*(?:async\s*)?\("
    )
    if not re.search(solve_pattern, code):
        errors.append("Define the required `solve` function.")
    for pattern, message in JAVASCRIPT_BLOCKED_PATTERNS:
        if re.search(pattern, code):
            errors.append(message)
    return list(dict.fromkeys(errors))


def _run_javascript_tests(
    code: str,
    tests: list[dict[str, Any]],
    timeout_seconds: int = 3,
) -> dict[str, Any]:
    validation_errors = validate_javascript_code(code)
    if validation_errors:
        return {
            "status": "validation_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": "\n".join(validation_errors),
            "stdout": "",
        }

    node_path = shutil.which("node")
    if not node_path:
        return {
            "status": "runner_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": "Node.js is not installed on this server.",
            "stdout": "",
        }

    runner_source = (
        "const USER_CODE = "
        + json.dumps(code)
        + ";\nconst TESTS = "
        + json.dumps(tests)
        + ";\n"
        + r'''
const vm = require("node:vm");
const logs = [];
const sandbox = {
    console: {
        log: (...values) => logs.push(values.map((value) => {
            if (typeof value === "string") return value;
            try { return JSON.stringify(value); }
            catch (_) { return String(value); }
        }).join(" "))
    }
};
vm.createContext(sandbox, {
    codeGeneration: { strings: false, wasm: false }
});

const payload = {
    status: "completed",
    passed: 0,
    total: TESTS.length,
    results: [],
    error: ""
};

const stable = (value) => {
    if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
    if (value && typeof value === "object") {
        return `{${Object.keys(value).sort().map(
            (key) => `${JSON.stringify(key)}:${stable(value[key])}`
        ).join(",")}}`;
    }
    return JSON.stringify(value);
};

const valuesMatch = (actual, expected, comparison) => {
    if (comparison === "float") {
        return Number.isFinite(Number(actual))
            && Number.isFinite(Number(expected))
            && Math.abs(Number(actual) - Number(expected)) <= 1e-5;
    }
    if (comparison === "unordered_nested") {
        if (!Array.isArray(actual) || !Array.isArray(expected)) return false;
        return stable(actual.map(stable).sort()) === stable(
            expected.map(stable).sort()
        );
    }
    return stable(actual) === stable(expected);
};

try {
    const source = USER_CODE
        + "\n;globalThis.__guidedSolve = "
        + "(typeof solve === 'function' ? solve : undefined);";
    new vm.Script(source, { filename: "learner.js" }).runInContext(
        sandbox,
        { timeout: 2000 }
    );
    if (typeof sandbox.__guidedSolve !== "function") {
        throw new TypeError("`solve` is not callable");
    }

    for (let index = 0; index < TESTS.length; index += 1) {
        const test = TESTS[index];
        const expected = JSON.parse(JSON.stringify(test.expected));
        sandbox.__guidedArgs = JSON.parse(JSON.stringify(test.args));
        try {
            const rawActual = new vm.Script(
                "__guidedSolve(...__guidedArgs)"
            ).runInContext(sandbox, { timeout: 2000 });
            const actual = rawActual === undefined
                ? null
                : JSON.parse(JSON.stringify(rawActual));
            const passed = valuesMatch(
                actual,
                expected,
                test.comparison || "exact"
            );
            if (passed) payload.passed += 1;
            payload.results.push({
                test: index + 1,
                passed,
                input: test.args,
                expected,
                actual,
                error: ""
            });
        } catch (error) {
            payload.results.push({
                test: index + 1,
                passed: false,
                input: test.args,
                expected,
                actual: null,
                error: String(error && error.stack ? error.stack : error)
            });
        }
    }
} catch (error) {
    payload.status = error && error.name === "SyntaxError"
        ? "validation_error"
        : "runtime_error";
    payload.error = String(error && error.stack ? error.stack : error);
}

payload.stdout = logs.join("\n").slice(-3000);
process.stdout.write(
    "__GUIDED_CODE_RESULT__" + JSON.stringify(payload)
);
'''
    )

    with tempfile.TemporaryDirectory(prefix="guided_code_js_") as temp_dir:
        runner_path = Path(temp_dir) / "runner.js"
        runner_path.write_text(runner_source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [node_path, "--no-warnings", str(runner_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "timeout",
                "passed": 0,
                "total": len(tests),
                "results": [],
                "error": f"Execution exceeded {timeout_seconds} seconds.",
                "stdout": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
            }

    stdout = completed.stdout or ""
    marker = "__GUIDED_CODE_RESULT__"
    marker_index = stdout.rfind(marker)
    if marker_index == -1:
        return {
            "status": "runner_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": (completed.stderr or "Runner did not return a valid result.")[-4000:],
            "stdout": stdout[-3000:],
        }

    raw_payload = stdout[marker_index + len(marker):].strip().splitlines()[0]
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return {
            "status": "runner_error",
            "passed": 0,
            "total": len(tests),
            "results": [],
            "error": "Runner returned malformed output.",
            "stdout": stdout[-3000:],
        }

    payload["stdout"] = str(payload.get("stdout") or "")[-3000:]
    if completed.returncode != 0 and payload.get("status") == "completed":
        payload["status"] = "runner_error"
        payload["error"] = (completed.stderr or "Process exited unexpectedly.")[-4000:]
    return payload


def run_tests(
    code: str,
    tests: list[dict[str, Any]],
    timeout_seconds: int = 3,
    language: str = "python",
) -> dict[str, Any]:
    if language == "python":
        return _run_python_tests(code, tests, timeout_seconds)
    if language == "javascript":
        return _run_javascript_tests(code, tests, timeout_seconds)
    return {
        "status": "unsupported_language",
        "passed": 0,
        "total": len(tests),
        "results": [],
        "error": "Local test execution is not configured for this language.",
        "stdout": "",
    }


def classify_mistake(result: dict[str, Any], code: str) -> tuple[str, str]:
    status = result.get("status")
    error = (result.get("error") or "").lower()

    if status == "validation_error" and "syntax" in error:
        return "Syntax", "The code cannot be parsed. Fix the reported syntax error first."
    if status == "validation_error":
        return "Submission format", "The required function or an allowed-language rule is missing."
    if status == "timeout":
        return "Complexity or infinite loop", "The program did not finish within the execution limit."
    if status in {"runtime_error", "runner_error"}:
        if "indexerror" in error:
            return "Boundary handling", "An index moved outside the valid range."
        if "keyerror" in error:
            return "Missing key case", "A dictionary lookup assumed that a key already existed."
        if "recursionerror" in error:
            return "Recursion depth", "The recursion did not reach a safe terminating state."
        if "typeerror" in error:
            return "Type or function contract", "A value or function signature does not match the expected contract."
        return "Runtime failure", "The program raised an exception before completing the tests."

    failed = [item for item in result.get("results", []) if not item.get("passed")]
    if not failed:
        return "Correct", "All available tests passed."

    first = failed[0]
    actual = first.get("actual")
    expected = first.get("expected")
    if actual is None and expected is not None:
        return "Missing return value", "The function may reach the end without returning the computed answer."
    if isinstance(expected, list) and isinstance(actual, list) and len(actual) != len(expected):
        return "Incomplete output", "The result has the wrong number of elements. Check loop boundaries and skipped cases."
    if any(token in code for token in ["range(len(", "while"]):
        return "Edge case or boundary", "The general approach may be close, but a boundary or state update fails on some inputs."
    return "Logic error", "The code runs, but at least one output differs from the expected result."
