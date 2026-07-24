from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class Language:
    id: str
    label: str
    editor_mode: str
    locally_runnable: bool


LANGUAGES = (
    Language("python", "Python", "python", True),
    Language("c", "C", "c_cpp", False),
    Language("cpp", "C++", "c_cpp", False),
    Language("csharp", "C#", "csharp", False),
    Language("java", "Java", "java", False),
    Language("javascript", "JavaScript", "javascript", True),
    Language("go", "Go", "golang", False),
)
LANGUAGE_BY_ID = {language.id: language for language in LANGUAGES}


@dataclass(frozen=True)
class TypeSpec:
    kind: str
    item: TypeSpec | None = None


UNKNOWN = TypeSpec("unknown")


def _merge_types(left: TypeSpec, right: TypeSpec) -> TypeSpec:
    if left == UNKNOWN:
        return right
    if right == UNKNOWN:
        return left
    if left.kind == right.kind:
        if left.kind != "list":
            return left
        return TypeSpec("list", _merge_types(left.item or UNKNOWN, right.item or UNKNOWN))
    if {left.kind, right.kind} == {"int", "float"}:
        return TypeSpec("float")
    return left


def _infer_value(value: Any) -> TypeSpec:
    if isinstance(value, bool):
        return TypeSpec("bool")
    if isinstance(value, int):
        return TypeSpec("int")
    if isinstance(value, float):
        return TypeSpec("float")
    if isinstance(value, str):
        return TypeSpec("string")
    if isinstance(value, list):
        item = UNKNOWN
        for member in value:
            item = _merge_types(item, _infer_value(member))
        return TypeSpec("list", item)
    return UNKNOWN


def _infer_values(values: Iterable[Any]) -> TypeSpec:
    inferred = UNKNOWN
    for value in values:
        inferred = _merge_types(inferred, _infer_value(value))
    return inferred


def _parameter_names(problem: dict[str, Any]) -> list[str]:
    signature = str(problem["signature"])
    tree = ast.parse(f"{signature}\n    pass\n")
    function = tree.body[0]
    if not isinstance(function, ast.FunctionDef):
        return []
    return [argument.arg for argument in function.args.args]


def _problem_types(problem: dict[str, Any]) -> tuple[list[str], list[TypeSpec], TypeSpec]:
    names = _parameter_names(problem)
    tests = problem.get("tests", [])
    parameters = [
        _infer_values(
            test.get("args", [])[index]
            for test in tests
            if index < len(test.get("args", []))
        )
        for index in range(len(names))
    ]
    result = _infer_values(test.get("expected") for test in tests)
    return names, parameters, result


def _nested_item(spec: TypeSpec) -> TypeSpec:
    return spec.item if spec.item and spec.item != UNKNOWN else TypeSpec("int")


def _cpp_type(spec: TypeSpec) -> str:
    scalar = {
        "bool": "bool",
        "int": "int",
        "float": "double",
        "string": "string",
        "unknown": "int",
    }
    if spec.kind != "list":
        return scalar[spec.kind]
    return f"vector<{_cpp_type(_nested_item(spec))}>"


def _java_type(spec: TypeSpec) -> str:
    scalar = {
        "bool": "boolean",
        "int": "int",
        "float": "double",
        "string": "String",
        "unknown": "Object",
    }
    if spec.kind != "list":
        return scalar[spec.kind]
    boxed = {
        "bool": "Boolean",
        "int": "Integer",
        "float": "Double",
        "string": "String",
        "unknown": "Object",
    }
    item = _nested_item(spec)
    item_type = _java_type(item) if item.kind == "list" else boxed[item.kind]
    return f"List<{item_type}>"


def _csharp_type(spec: TypeSpec) -> str:
    scalar = {
        "bool": "bool",
        "int": "int",
        "float": "double",
        "string": "string",
        "unknown": "object",
    }
    if spec.kind != "list":
        return scalar[spec.kind]
    return f"List<{_csharp_type(_nested_item(spec))}>"


def _go_type(spec: TypeSpec) -> str:
    scalar = {
        "bool": "bool",
        "int": "int",
        "float": "float64",
        "string": "string",
        "unknown": "any",
    }
    if spec.kind != "list":
        return scalar[spec.kind]
    return f"[]{_go_type(_nested_item(spec))}"


def _c_type(spec: TypeSpec) -> str:
    scalar = {
        "bool": "bool",
        "int": "int",
        "float": "double",
        "string": "const char *",
        "unknown": "void *",
    }
    if spec.kind != "list":
        return scalar[spec.kind]
    item = _nested_item(spec)
    if item.kind == "list":
        nested = _nested_item(item)
        return "StringMatrix" if nested.kind == "string" else "IntMatrix"
    return "StringArray" if item.kind == "string" else "IntArray"


def _default_value(spec: TypeSpec, language: str) -> str:
    if language == "cpp":
        return {
            "bool": "false",
            "int": "0",
            "float": "0.0",
            "string": '""',
            "list": "{}",
            "unknown": "{}",
        }[spec.kind]
    if language == "java":
        return {
            "bool": "false",
            "int": "0",
            "float": "0.0",
            "string": '""',
            "list": "new ArrayList<>()",
            "unknown": "null",
        }[spec.kind]
    if language == "csharp":
        return {
            "bool": "false",
            "int": "0",
            "float": "0.0",
            "string": '""',
            "list": f"new {_csharp_type(spec)}()",
            "unknown": "null",
        }[spec.kind]
    if language == "go":
        return {
            "bool": "false",
            "int": "0",
            "float": "0",
            "string": '""',
            "list": "nil",
            "unknown": "nil",
        }[spec.kind]
    if language == "c":
        if spec.kind == "list":
            return f"({_c_type(spec)}){{NULL, 0}}"
        return {
            "bool": "false",
            "int": "0",
            "float": "0.0",
            "string": "NULL",
            "unknown": "NULL",
        }[spec.kind]
    return ""


def starter_code(problem: dict[str, Any], language_id: str) -> str:
    if language_id == "python":
        return str(problem["starter_code"])

    names, parameter_types, result_type = _problem_types(problem)
    if language_id == "javascript":
        parameters = ", ".join(names)
        return (
            f"function solve({parameters}) {{\n"
            "    // Write your solution here\n"
            "}\n"
        )

    if language_id == "cpp":
        parameters = ", ".join(
            f"{_cpp_type(spec)} {name}"
            for name, spec in zip(names, parameter_types)
        )
        return (
            "#include <string>\n"
            "#include <vector>\n"
            "using namespace std;\n\n"
            "class Solution {\n"
            "public:\n"
            f"    {_cpp_type(result_type)} solve({parameters}) {{\n"
            "        // Write your solution here\n"
            f"        return {_default_value(result_type, 'cpp')};\n"
            "    }\n"
            "};\n"
        )

    if language_id == "java":
        parameters = ", ".join(
            f"{_java_type(spec)} {name}"
            for name, spec in zip(names, parameter_types)
        )
        return (
            "import java.util.*;\n\n"
            "class Solution {\n"
            f"    public {_java_type(result_type)} solve({parameters}) {{\n"
            "        // Write your solution here\n"
            f"        return {_default_value(result_type, 'java')};\n"
            "    }\n"
            "}\n"
        )

    if language_id == "csharp":
        parameters = ", ".join(
            f"{_csharp_type(spec)} {name}"
            for name, spec in zip(names, parameter_types)
        )
        return (
            "using System.Collections.Generic;\n\n"
            "public class Solution\n"
            "{\n"
            f"    public {_csharp_type(result_type)} Solve({parameters})\n"
            "    {\n"
            "        // Write your solution here\n"
            f"        return {_default_value(result_type, 'csharp')};\n"
            "    }\n"
            "}\n"
        )

    if language_id == "go":
        parameters = ", ".join(
            f"{name} {_go_type(spec)}"
            for name, spec in zip(names, parameter_types)
        )
        return (
            "package main\n\n"
            f"func solve({parameters}) {_go_type(result_type)} {{\n"
            "    // Write your solution here\n"
            f"    return {_default_value(result_type, 'go')}\n"
            "}\n"
        )

    if language_id == "c":
        parameters = ", ".join(
            f"{_c_type(spec)} {name}"
            for name, spec in zip(names, parameter_types)
        ) or "void"
        return (
            "#include <stdbool.h>\n"
            "#include <stddef.h>\n\n"
            "typedef struct { int *data; size_t length; } IntArray;\n"
            "typedef struct { IntArray *data; size_t length; } IntMatrix;\n"
            "typedef struct { const char **data; size_t length; } StringArray;\n"
            "typedef struct { StringArray *data; size_t length; } StringMatrix;\n\n"
            f"{_c_type(result_type)} solve({parameters}) {{\n"
            "    // Write your solution here\n"
            f"    return {_default_value(result_type, 'c')};\n"
            "}\n"
        )

    raise ValueError(f"Unknown language: {language_id}")
