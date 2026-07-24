from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Iterable

from core.leetcode_methods import METHOD_BY_PROBLEM_ID, PARAMETERS_BY_PROBLEM_ID


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
    nullable: bool = False


UNKNOWN = TypeSpec("unknown")
NONE = TypeSpec("none")


IN_PLACE_ARGUMENT_BY_ID: dict[str, int] = {
    "move-zeroes": 0,
    "rotate-matrix": 0,
    "set-matrix-zeroes": 0,
    "leetcode-31-next-permutation": 0,
    "leetcode-37-sudoku-solver": 0,
    "leetcode-48-rotate-image": 0,
    "leetcode-75-sort-colors": 0,
    "leetcode-88-merge-sorted-array": 0,
    "leetcode-99-recover-binary-search-tree": 0,
    "leetcode-114-flatten-binary-tree-to-linked-list": 0,
    "leetcode-130-surrounded-regions": 0,
    "leetcode-143-reorder-list": 0,
    "leetcode-189-rotate-array": 0,
    "leetcode-286-walls-and-gates": 0,
}


def _merge_types(left: TypeSpec, right: TypeSpec) -> TypeSpec:
    if left == UNKNOWN:
        return right
    if right == UNKNOWN:
        return left
    if left.kind == "none":
        return TypeSpec(right.kind, right.item, True)
    if right.kind == "none":
        return TypeSpec(left.kind, left.item, True)
    if left.kind == right.kind:
        if left.kind != "list":
            return TypeSpec(left.kind, nullable=left.nullable or right.nullable)
        return TypeSpec(
            "list",
            _merge_types(left.item or UNKNOWN, right.item or UNKNOWN),
            left.nullable or right.nullable,
        )
    if {left.kind, right.kind} == {"int", "float"}:
        return TypeSpec("float", nullable=left.nullable or right.nullable)
    return TypeSpec(left.kind, left.item, left.nullable or right.nullable)


def _infer_value(value: Any) -> TypeSpec:
    if value is None:
        return NONE
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
    try:
        tree = ast.parse(f"{signature}\n    pass\n")
    except SyntaxError:
        return []
    function = tree.body[0]
    if not isinstance(function, ast.FunctionDef):
        return []
    fallback = [argument.arg for argument in function.args.args]
    canonical = PARAMETERS_BY_PROBLEM_ID.get(str(problem["id"]))
    if canonical and len(canonical) == len(fallback):
        return list(canonical)
    return fallback


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
    result = (
        NONE
        if str(problem["id"]) in IN_PLACE_ARGUMENT_BY_ID
        else _infer_values(test.get("expected") for test in tests)
    )
    return names, parameters, result


def _is_design_problem(problem: dict[str, Any]) -> bool:
    tests = problem.get("tests", [])
    if not tests:
        return False
    args = tests[0].get("args", [])
    expected = tests[0].get("expected")
    return (
        len(args) >= 2
        and isinstance(args[0], list)
        and bool(args[0])
        and all(isinstance(operation, str) for operation in args[0])
        and isinstance(args[1], list)
        and len(args[0]) == len(args[1])
        and isinstance(expected, list)
        and len(expected) == len(args[0])
    )


DESIGN_PARAMETER_NAMES: dict[tuple[str, str], tuple[str, ...]] = {
    ("RandomizedSet", "__init__"): (), ("RandomizedSet", "insert"): ("val",),
    ("RandomizedSet", "remove"): ("val",), ("RandomizedSet", "getRandom"): (),
    ("TimeMap", "__init__"): (), ("TimeMap", "set"): ("key", "value", "timestamp"),
    ("TimeMap", "get"): ("key", "timestamp"),
    ("SnapshotArray", "__init__"): ("length",), ("SnapshotArray", "set"): ("index", "val"),
    ("SnapshotArray", "snap"): (), ("SnapshotArray", "get"): ("index", "snap_id"),
    ("KthLargest", "__init__"): ("k", "nums"), ("KthLargest", "add"): ("val",),
    ("Twitter", "__init__"): (), ("Twitter", "postTweet"): ("userId", "tweetId"),
    ("Twitter", "getNewsFeed"): ("userId",), ("Twitter", "follow"): ("followerId", "followeeId"),
    ("Twitter", "unfollow"): ("followerId", "followeeId"),
    ("MedianFinder", "__init__"): (), ("MedianFinder", "addNum"): ("num",),
    ("MedianFinder", "findMedian"): (),
    ("MyCalendar", "__init__"): (), ("MyCalendar", "book"): ("startTime", "endTime"),
    ("LRUCache", "__init__"): ("capacity",), ("LRUCache", "get"): ("key",),
    ("LRUCache", "put"): ("key", "value"),
    ("LFUCache", "__init__"): ("capacity",), ("LFUCache", "get"): ("key",),
    ("LFUCache", "put"): ("key", "value"),
    ("MyLinkedList", "__init__"): (), ("MyLinkedList", "get"): ("index",),
    ("MyLinkedList", "addAtHead"): ("val",), ("MyLinkedList", "addAtTail"): ("val",),
    ("MyLinkedList", "addAtIndex"): ("index", "val"), ("MyLinkedList", "deleteAtIndex"): ("index",),
    ("BrowserHistory", "__init__"): ("homepage",), ("BrowserHistory", "visit"): ("url",),
    ("BrowserHistory", "back"): ("steps",), ("BrowserHistory", "forward"): ("steps",),
    ("DetectSquares", "__init__"): (), ("DetectSquares", "add"): ("point",),
    ("DetectSquares", "count"): ("point",),
    ("MinStack", "__init__"): (), ("MinStack", "push"): ("val",),
    ("MinStack", "pop"): (), ("MinStack", "top"): (), ("MinStack", "getMin"): (),
    ("Vector2D", "__init__"): ("vec",), ("Vector2D", "next"): (), ("Vector2D", "hasNext"): (),
    ("FreqStack", "__init__"): (), ("FreqStack", "push"): ("val",), ("FreqStack", "pop"): (),
    ("BSTIterator", "__init__"): ("root",), ("BSTIterator", "next"): (), ("BSTIterator", "hasNext"): (),
    ("Trie", "__init__"): (), ("Trie", "insert"): ("word",), ("Trie", "search"): ("word",),
    ("Trie", "startsWith"): ("prefix",),
    ("WordDictionary", "__init__"): (), ("WordDictionary", "addWord"): ("word",),
    ("WordDictionary", "search"): ("word",),
    ("NumArray", "__init__"): ("nums",), ("NumArray", "sumRange"): ("left", "right"),
    ("ProductOfNumbers", "__init__"): (), ("ProductOfNumbers", "add"): ("num",),
    ("ProductOfNumbers", "getProduct"): ("k",),
    ("MyStack", "__init__"): (), ("MyStack", "push"): ("x",), ("MyStack", "pop"): (),
    ("MyStack", "top"): (), ("MyStack", "empty"): (),
    ("MyQueue", "__init__"): (), ("MyQueue", "push"): ("x",), ("MyQueue", "pop"): (),
    ("MyQueue", "peek"): (), ("MyQueue", "empty"): (),
    ("PeekingIterator", "__init__"): ("iterator",), ("PeekingIterator", "peek"): (),
    ("PeekingIterator", "next"): (), ("PeekingIterator", "hasNext"): (),
    ("HitCounter", "__init__"): (), ("HitCounter", "hit"): ("timestamp",),
    ("HitCounter", "getHits"): ("timestamp",),
    ("TicTacToe", "__init__"): ("n",), ("TicTacToe", "move"): ("row", "col", "player"),
}


DESIGN_PARAMETER_NAMES_BY_PROBLEM: dict[tuple[str, str], tuple[str, ...]] = {
    ("leetcode-528-random-pick-with-weight", "__init__"): ("w",),
    ("leetcode-398-random-pick-index", "__init__"): ("nums",),
    ("leetcode-398-random-pick-index", "pick"): ("target",),
}


def _safe_names(problem_id: str, class_name: str, method_name: str, count: int) -> list[str]:
    configured = DESIGN_PARAMETER_NAMES_BY_PROBLEM.get(
        (problem_id, method_name),
        DESIGN_PARAMETER_NAMES.get((class_name, method_name), ()),
    )
    if len(configured) == count:
        return list(configured)
    return [f"arg{index + 1}" for index in range(count)]


def _design_method_specs(problem: dict[str, Any]) -> list[dict[str, Any]]:
    tests = problem["tests"]
    operations = tests[0]["args"][0]
    class_name = operations[0]
    ordered_methods = ["__init__"]
    for operation in operations[1:]:
        if operation not in ordered_methods:
            ordered_methods.append(operation)

    specs: list[dict[str, Any]] = []
    for operation in ordered_methods:
        argument_sets: list[list[Any]] = []
        returns: list[Any] = []
        for test in tests:
            test_operations, test_arguments = test["args"][:2]
            expected = test["expected"]
            for index, current in enumerate(test_operations):
                normalized = "__init__" if index == 0 else current
                if normalized != operation:
                    continue
                argument_sets.append(test_arguments[index])
                returns.append(None if index == 0 else expected[index])
        count = max((len(args) for args in argument_sets), default=0)
        specs.append({
            "name": operation,
            "parameter_names": _safe_names(str(problem["id"]), class_name, operation, count),
            "parameter_types": [
                _infer_values(args[index] for args in argument_sets if index < len(args))
                for index in range(count)
            ],
            "return_type": NONE if operation == "__init__" else _infer_values(returns),
        })
    return specs


SPECIAL_KIND_BY_ID = {
    "leetcode-271-encode-and-decode-strings": "codec_strings",
    "leetcode-297-serialize-and-deserialize-binary-tree": "codec_tree",
    "leetcode-428-serialize-and-deserialize-n-ary-tree": "codec_tree",
    "leetcode-341-flatten-nested-list-iterator": "nested_iterator",
    "leetcode-1570-dot-product-of-two-sparse-vectors": "sparse_vector",
}


def execution_contract(problem: dict[str, Any]) -> dict[str, Any]:
    problem_id = str(problem["id"])
    special_kind = SPECIAL_KIND_BY_ID.get(problem_id)
    if special_kind == "codec_strings":
        return {"kind": special_kind, "class_name": "Codec", "methods": ["encode", "decode"]}
    if special_kind == "codec_tree":
        return {"kind": special_kind, "class_name": "Codec", "methods": ["serialize", "deserialize"]}
    if special_kind == "nested_iterator":
        return {"kind": special_kind, "class_name": "NestedIterator", "methods": ["next", "hasNext"]}
    if special_kind == "sparse_vector":
        return {"kind": special_kind, "class_name": "SparseVector", "methods": ["dotProduct"]}
    if _is_design_problem(problem):
        class_name = problem["tests"][0]["args"][0][0]
        return {
            "kind": "design",
            "class_name": class_name,
            "methods": [spec["name"] for spec in _design_method_specs(problem) if spec["name"] != "__init__"],
        }
    contract = {
        "kind": "solution",
        "class_name": "Solution",
        "method_name": METHOD_BY_PROBLEM_ID[problem_id],
        "methods": [METHOD_BY_PROBLEM_ID[problem_id]],
    }
    if problem_id in IN_PLACE_ARGUMENT_BY_ID:
        contract["in_place_arg_index"] = IN_PLACE_ARGUMENT_BY_ID[problem_id]
    return contract


def _nested_item(spec: TypeSpec) -> TypeSpec:
    return spec.item if spec.item and spec.item != UNKNOWN else TypeSpec("int")


def _python_type(spec: TypeSpec) -> str:
    scalar = {"bool": "bool", "int": "int", "float": "float", "string": "str", "none": "None", "unknown": "Any"}
    result = scalar.get(spec.kind)
    if spec.kind == "list":
        result = f"List[{_python_type(_nested_item(spec))}]"
    assert result is not None
    if spec.nullable and result != "None":
        result = f"Optional[{result}]"
    return result


def _javascript_type(spec: TypeSpec) -> str:
    scalar = {"bool": "boolean", "int": "number", "float": "number", "string": "string", "none": "void", "unknown": "*"}
    if spec.kind == "list":
        inner = _javascript_type(_nested_item(spec))
        return f"Array<{inner}>"
    return scalar[spec.kind]


def _cpp_type(spec: TypeSpec) -> str:
    scalar = {"bool": "bool", "int": "int", "float": "double", "string": "string", "none": "void", "unknown": "int"}
    result = f"vector<{_cpp_type(_nested_item(spec))}>" if spec.kind == "list" else scalar[spec.kind]
    if spec.nullable and spec.kind not in {"none", "unknown"}:
        result = f"optional<{result}>"
    return result


def _java_type(spec: TypeSpec) -> str:
    scalar = {"bool": "boolean", "int": "int", "float": "double", "string": "String", "none": "void", "unknown": "Object"}
    boxed = {"bool": "Boolean", "int": "Integer", "float": "Double", "string": "String", "none": "Void", "unknown": "Object"}
    if spec.kind == "list":
        item = _nested_item(spec)
        item_type = _java_type(item) if item.kind == "list" else boxed[item.kind]
        return f"List<{item_type}>"
    return boxed[spec.kind] if spec.nullable and spec.kind not in {"none", "unknown"} else scalar[spec.kind]


def _csharp_type(spec: TypeSpec) -> str:
    scalar = {"bool": "bool", "int": "int", "float": "double", "string": "string", "none": "void", "unknown": "object"}
    result = f"List<{_csharp_type(_nested_item(spec))}>" if spec.kind == "list" else scalar[spec.kind]
    if spec.nullable and spec.kind in {"bool", "int", "float"}:
        result += "?"
    return result


def _go_type(spec: TypeSpec) -> str:
    scalar = {"bool": "bool", "int": "int", "float": "float64", "string": "string", "none": "", "unknown": "any"}
    return f"[]{_go_type(_nested_item(spec))}" if spec.kind == "list" else scalar[spec.kind]


def _c_type(spec: TypeSpec) -> str:
    scalar = {"bool": "bool", "int": "int", "float": "double", "string": "const char *", "none": "void", "unknown": "void *"}
    if spec.kind != "list":
        return scalar[spec.kind]
    item = _nested_item(spec)
    if item.kind == "list":
        return "StringMatrix" if _nested_item(item).kind == "string" else "IntMatrix"
    return "StringArray" if item.kind == "string" else "IntArray"


def _default_value(spec: TypeSpec, language: str) -> str | None:
    if spec.kind == "none":
        return None
    defaults = {
        "cpp": {"bool": "false", "int": "0", "float": "0.0", "string": '\"\"', "list": "{}", "unknown": "{}"},
        "java": {"bool": "false", "int": "0", "float": "0.0", "string": '\"\"', "list": "new ArrayList<>()", "unknown": "null"},
        "csharp": {"bool": "false", "int": "0", "float": "0.0", "string": '\"\"', "list": f"new {_csharp_type(spec)}()", "unknown": "null"},
        "go": {"bool": "false", "int": "0", "float": "0", "string": '\"\"', "list": "nil", "unknown": "nil"},
        "c": {"bool": "false", "int": "0", "float": "0.0", "string": "NULL", "list": f"({_c_type(spec)}){{NULL, 0}}", "unknown": "NULL"},
    }
    return defaults[language][spec.kind]


def _python_header(specs: Iterable[TypeSpec]) -> str:
    rendered = " ".join(_python_type(spec) for spec in specs)
    imports = []
    if "List[" in rendered:
        imports.append("List")
    if "Optional[" in rendered:
        imports.append("Optional")
    if "Any" in rendered:
        imports.append("Any")
    return f"from typing import {', '.join(imports)}\n\n" if imports else ""


def _solution_starter(problem: dict[str, Any], language_id: str) -> str:
    names, parameter_types, result_type = _problem_types(problem)
    method = METHOD_BY_PROBLEM_ID[str(problem["id"])]
    if language_id == "python":
        header = _python_header([*parameter_types, result_type])
        params = ", ".join(f"{name}: {_python_type(spec)}" for name, spec in zip(names, parameter_types))
        return f"{header}class Solution:\n    def {method}(self, {params}) -> {_python_type(result_type)}:\n        # Write your solution here\n        pass\n".replace("self, )", "self)")
    if language_id == "javascript":
        docs = ["/**"] + [f" * @param {{{_javascript_type(spec)}}} {name}" for name, spec in zip(names, parameter_types)] + [f" * @return {{{_javascript_type(result_type)}}}", " */"]
        return "\n".join(docs) + f"\nvar {method} = function({', '.join(names)}) {{\n    // Write your solution here\n}};\n"
    if language_id == "cpp":
        params = ", ".join(f"{_cpp_type(spec)} {name}" for name, spec in zip(names, parameter_types))
        default = _default_value(result_type, "cpp")
        return "#include <optional>\n#include <string>\n#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n" + f"    {_cpp_type(result_type)} {method}({params}) {{\n        // Write your solution here\n" + (f"        return {default};\n" if default is not None else "") + "    }\n};\n"
    if language_id == "java":
        params = ", ".join(f"{_java_type(spec)} {name}" for name, spec in zip(names, parameter_types))
        default = _default_value(result_type, "java")
        return "import java.util.*;\n\nclass Solution {\n" + f"    public {_java_type(result_type)} {method}({params}) {{\n        // Write your solution here\n" + (f"        return {default};\n" if default is not None else "") + "    }\n}\n"
    if language_id == "csharp":
        params = ", ".join(f"{_csharp_type(spec)} {name}" for name, spec in zip(names, parameter_types))
        csharp_method = method[:1].upper() + method[1:]
        default = _default_value(result_type, "csharp")
        return "using System.Collections.Generic;\n\npublic class Solution\n{\n" + f"    public {_csharp_type(result_type)} {csharp_method}({params})\n    {{\n        // Write your solution here\n" + (f"        return {default};\n" if default is not None else "") + "    }\n}\n"
    if language_id == "go":
        params = ", ".join(f"{name} {_go_type(spec)}" for name, spec in zip(names, parameter_types))
        return_type = _go_type(result_type)
        default = _default_value(result_type, "go")
        return "package main\n\n" + f"func {method}({params})" + (f" {return_type}" if return_type else "") + " {\n    // Write your solution here\n" + (f"    return {default}\n" if default is not None else "") + "}\n"
    if language_id == "c":
        params = ", ".join(f"{_c_type(spec)} {name}" for name, spec in zip(names, parameter_types)) or "void"
        default = _default_value(result_type, "c")
        return "#include <stdbool.h>\n#include <stddef.h>\n\ntypedef struct { int *data; size_t length; } IntArray;\ntypedef struct { IntArray *data; size_t length; } IntMatrix;\ntypedef struct { const char **data; size_t length; } StringArray;\ntypedef struct { StringArray *data; size_t length; } StringMatrix;\n\n" + f"{_c_type(result_type)} {method}({params}) {{\n    // Write your solution here\n" + (f"    return {default};\n" if default is not None else "") + "}\n"
    raise ValueError(f"Unknown language: {language_id}")


def _design_starter(problem: dict[str, Any], language_id: str) -> str:
    class_name = problem["tests"][0]["args"][0][0]
    specs = _design_method_specs(problem)
    all_types = [spec for method in specs for spec in [*method["parameter_types"], method["return_type"]]]
    if language_id == "python":
        header = _python_header(all_types)
        lines = ([header.rstrip(), ""] if header else []) + [f"class {class_name}:"]
        for method in specs:
            name = "__init__" if method["name"] == "__init__" else method["name"]
            params = ", ".join(f"{n}: {_python_type(t)}" for n, t in zip(method["parameter_names"], method["parameter_types"]))
            lines += [f"    def {name}(self{', ' if params else ''}{params}) -> {_python_type(method['return_type'])}:", "        # Write your solution here", "        pass", ""]
        return "\n".join(lines).strip() + "\n"
    if language_id == "javascript":
        constructor = specs[0]
        params = ", ".join(constructor["parameter_names"])
        lines = [f"var {class_name} = function({params}) {{", "    // Initialize your data structure here", "};", ""]
        for method in specs[1:]:
            docs = ["/**"] + [f" * @param {{{_javascript_type(t)}}} {n}" for n, t in zip(method["parameter_names"], method["parameter_types"])] + [f" * @return {{{_javascript_type(method['return_type'])}}}", " */"]
            lines += docs + [f"{class_name}.prototype.{method['name']} = function({', '.join(method['parameter_names'])}) {{", "    // Write your solution here", "};", ""]
        return "\n".join(lines).rstrip() + "\n"
    # For compiled languages, emit the same class contract with typed methods.
    if language_id == "cpp":
        lines = ["#include <optional>", "#include <string>", "#include <vector>", "using namespace std;", "", f"class {class_name} {{", "public:"]
        for method in specs:
            params = ", ".join(f"{_cpp_type(t)} {n}" for n, t in zip(method["parameter_names"], method["parameter_types"]))
            if method["name"] == "__init__": lines += [f"    {class_name}({params}) {{", "        // Initialize your data structure here", "    }"]
            else:
                default = _default_value(method["return_type"], "cpp")
                lines += [f"    {_cpp_type(method['return_type'])} {method['name']}({params}) {{", "        // Write your solution here"] + ([f"        return {default};"] if default is not None else []) + ["    }"]
        return "\n".join(lines + ["};", ""])
    if language_id == "java":
        lines = ["import java.util.*;", "", f"class {class_name} {{"]
        for method in specs:
            params = ", ".join(f"{_java_type(t)} {n}" for n, t in zip(method["parameter_names"], method["parameter_types"]))
            if method["name"] == "__init__": lines += [f"    public {class_name}({params}) {{", "        // Initialize your data structure here", "    }"]
            else:
                default = _default_value(method["return_type"], "java")
                lines += [f"    public {_java_type(method['return_type'])} {method['name']}({params}) {{", "        // Write your solution here"] + ([f"        return {default};"] if default is not None else []) + ["    }"]
        return "\n".join(lines + ["}", ""])
    if language_id == "csharp":
        lines = ["using System.Collections.Generic;", "", f"public class {class_name}", "{"]
        for method in specs:
            params = ", ".join(f"{_csharp_type(t)} {n}" for n, t in zip(method["parameter_names"], method["parameter_types"]))
            if method["name"] == "__init__": lines += [f"    public {class_name}({params})", "    {", "        // Initialize your data structure here", "    }"]
            else:
                method_name = method["name"][:1].upper() + method["name"][1:]
                default = _default_value(method["return_type"], "csharp")
                lines += [f"    public {_csharp_type(method['return_type'])} {method_name}({params})", "    {", "        // Write your solution here"] + ([f"        return {default};"] if default is not None else []) + ["    }"]
        return "\n".join(lines + ["}", ""])
    # Go and C do not support classes; use a LeetCode-style object type plus methods.
    if language_id == "go":
        lines = ["package main", "", f"type {class_name} struct {{", "    // Add fields here", "}", ""]
        constructor = specs[0]
        params = ", ".join(f"{n} {_go_type(t)}" for n, t in zip(constructor["parameter_names"], constructor["parameter_types"]))
        lines += [f"func Constructor({params}) {class_name} {{", f"    return {class_name}{{}}", "}", ""]
        for method in specs[1:]:
            params = ", ".join(f"{n} {_go_type(t)}" for n, t in zip(method["parameter_names"], method["parameter_types"]))
            return_type = _go_type(method["return_type"]); default = _default_value(method["return_type"], "go")
            lines += [f"func (obj *{class_name}) {method['name'][:1].upper() + method['name'][1:]}({params})" + (f" {return_type}" if return_type else "") + " {", "    // Write your solution here"] + ([f"    return {default}"] if default is not None else []) + ["}", ""]
        return "\n".join(lines).rstrip() + "\n"
    if language_id == "c":
        # C has no classes; provide an explicit object API with typed functions.
        lines = ["#include <stdbool.h>", "#include <stddef.h>", "", f"typedef struct {class_name} {class_name};", ""]
        constructor = specs[0]
        params = ", ".join(f"{_c_type(t)} {n}" for n, t in zip(constructor["parameter_names"], constructor["parameter_types"])) or "void"
        lines += [f"{class_name} *{class_name}Create({params});"]
        for method in specs[1:]:
            params = [f"{class_name} *obj"] + [f"{_c_type(t)} {n}" for n, t in zip(method["parameter_names"], method["parameter_types"])]
            lines += [f"{_c_type(method['return_type'])} {class_name}{method['name'][:1].upper() + method['name'][1:]}({', '.join(params)});"]
        lines += [f"void {class_name}Free({class_name} *obj);", ""]
        return "\n".join(lines)
    raise ValueError(f"Unknown language: {language_id}")


def _special_starter(problem: dict[str, Any], language_id: str, kind: str) -> str:
    if kind.startswith("codec"):
        first, second = ("encode", "decode") if kind == "codec_strings" else ("serialize", "deserialize")
        value_spec = (
            TypeSpec("list", TypeSpec("string"))
            if kind == "codec_strings"
            else TypeSpec("list", TypeSpec("int", nullable=True))
        )
        py_value = _python_type(value_spec)
        js_value = _javascript_type(value_spec)
        cpp_value = _cpp_type(value_spec)
        java_value = _java_type(value_spec)
        csharp_value = _csharp_type(value_spec)
        go_value = _go_type(value_spec)
        c_value = _c_type(value_spec)
        value_name = "strs" if kind == "codec_strings" else "root"

        if language_id == "python":
            return (
                _python_header([value_spec])
                + "class Codec:\n"
                + f"    def {first}(self, {value_name}: {py_value}) -> str:\n"
                + "        # Write your solution here\n        pass\n\n"
                + f"    def {second}(self, data: str) -> {py_value}:\n"
                + "        # Write your solution here\n        pass\n"
            )
        if language_id == "javascript":
            return (
                "var Codec = function() {};\n\n"
                + f"/**\n * @param {{{js_value}}} {value_name}\n * @return {{string}}\n */\n"
                + f"Codec.prototype.{first} = function({value_name}) {{\n"
                + "    // Write your solution here\n};\n\n"
                + f"/**\n * @param {{string}} data\n * @return {{{js_value}}}\n */\n"
                + f"Codec.prototype.{second} = function(data) {{\n"
                + "    // Write your solution here\n};\n"
            )
        if language_id == "cpp":
            return (
                "#include <optional>\n#include <string>\n#include <vector>\nusing namespace std;\n\n"
                "class Codec {\npublic:\n"
                + f"    string {first}({cpp_value} {value_name}) {{\n"
                + "        // Write your solution here\n        return \"\";\n    }\n\n"
                + f"    {cpp_value} {second}(string data) {{\n"
                + "        // Write your solution here\n        return {};\n    }\n};\n"
            )
        if language_id == "java":
            return (
                "import java.util.*;\n\nclass Codec {\n"
                + f"    public String {first}({java_value} {value_name}) {{\n"
                + "        // Write your solution here\n        return \"\";\n    }\n\n"
                + f"    public {java_value} {second}(String data) {{\n"
                + "        // Write your solution here\n        return new ArrayList<>();\n    }\n}\n"
            )
        if language_id == "csharp":
            first_cs, second_cs = first[:1].upper() + first[1:], second[:1].upper() + second[1:]
            return (
                "using System.Collections.Generic;\n\npublic class Codec\n{\n"
                + f"    public string {first_cs}({csharp_value} {value_name})\n    {{\n"
                + "        // Write your solution here\n        return \"\";\n    }\n\n"
                + f"    public {csharp_value} {second_cs}(string data)\n    {{\n"
                + f"        // Write your solution here\n        return new {csharp_value}();\n    }}\n}}\n"
            )
        if language_id == "go":
            first_go, second_go = first[:1].upper() + first[1:], second[:1].upper() + second[1:]
            return (
                "package main\n\ntype Codec struct{}\n\nfunc Constructor() Codec {\n    return Codec{}\n}\n\n"
                + f"func (obj *Codec) {first_go}({value_name} {go_value}) string {{\n"
                + "    // Write your solution here\n    return \"\"\n}\n\n"
                + f"func (obj *Codec) {second_go}(data string) {go_value} {{\n"
                + "    // Write your solution here\n    return nil\n}\n"
            )
        if language_id == "c":
            first_c, second_c = first[:1].upper() + first[1:], second[:1].upper() + second[1:]
            return (
                "#include <stddef.h>\n\n"
                "typedef struct { int *data; size_t length; } IntArray;\n"
                "typedef struct { IntArray *data; size_t length; } IntMatrix;\n"
                "typedef struct { const char **data; size_t length; } StringArray;\n"
                "typedef struct { StringArray *data; size_t length; } StringMatrix;\n"
                "typedef struct Codec Codec;\n\n"
                "Codec *codecCreate(void);\n"
                + f"const char *codec{first_c}(Codec *obj, {c_value} {value_name});\n"
                + f"{c_value} codec{second_c}(Codec *obj, const char *data);\n"
                "void codecFree(Codec *obj);\n"
            )

    if kind == "nested_iterator":
        if language_id == "python":
            return (
                "from typing import Any, List\n\n"
                "class NestedIterator:\n"
                "    def __init__(self, nestedList: List[Any]):\n"
                "        # Initialize the iterator here\n        pass\n\n"
                "    def next(self) -> int:\n"
                "        # Return the next integer\n        pass\n\n"
                "    def hasNext(self) -> bool:\n"
                "        # Return whether another integer exists\n        pass\n"
            )
        if language_id == "javascript":
            return (
                "var NestedIterator = function(nestedList) {\n"
                "    // Initialize the iterator here\n};\n\n"
                "NestedIterator.prototype.next = function() {\n"
                "    // Return the next integer\n};\n\n"
                "NestedIterator.prototype.hasNext = function() {\n"
                "    // Return whether another integer exists\n};\n"
            )
        if language_id == "cpp":
            return (
                "#include <vector>\nusing namespace std;\n\n"
                "class NestedIterator {\npublic:\n"
                "    NestedIterator(vector<vector<int>> nestedList) {\n"
                "        // Initialize the iterator here\n    }\n\n"
                "    int next() {\n        // Return the next integer\n        return 0;\n    }\n\n"
                "    bool hasNext() {\n        // Return whether another integer exists\n        return false;\n    }\n};\n"
            )
        if language_id == "java":
            return (
                "import java.util.*;\n\nclass NestedIterator {\n"
                "    public NestedIterator(List<Object> nestedList) {\n"
                "        // Initialize the iterator here\n    }\n\n"
                "    public int next() {\n        return 0;\n    }\n\n"
                "    public boolean hasNext() {\n        return false;\n    }\n}\n"
            )
        if language_id == "csharp":
            return (
                "using System.Collections.Generic;\n\npublic class NestedIterator\n{\n"
                "    public NestedIterator(IList<object> nestedList)\n    {\n"
                "        // Initialize the iterator here\n    }\n\n"
                "    public int Next()\n    {\n        return 0;\n    }\n\n"
                "    public bool HasNext()\n    {\n        return false;\n    }\n}\n"
            )
        if language_id == "go":
            return (
                "package main\n\ntype NestedIterator struct{}\n\n"
                "func Constructor(nestedList []any) NestedIterator {\n    return NestedIterator{}\n}\n\n"
                "func (obj *NestedIterator) Next() int {\n    return 0\n}\n\n"
                "func (obj *NestedIterator) HasNext() bool {\n    return false\n}\n"
            )
        if language_id == "c":
            return (
                "#include <stdbool.h>\n#include <stddef.h>\n\n"
                "typedef struct NestedIterator NestedIterator;\n"
                "NestedIterator *nestedIteratorCreate(void *nestedList, size_t nestedListSize);\n"
                "int nestedIteratorNext(NestedIterator *obj);\n"
                "bool nestedIteratorHasNext(NestedIterator *obj);\n"
                "void nestedIteratorFree(NestedIterator *obj);\n"
            )

    if kind == "sparse_vector":
        if language_id == "python":
            return (
                "from typing import List\n\nclass SparseVector:\n"
                "    def __init__(self, nums: List[int]):\n"
                "        # Initialize your sparse representation here\n        pass\n\n"
                "    def dotProduct(self, vec: \"SparseVector\") -> int:\n"
                "        # Write your solution here\n        pass\n"
            )
        if language_id == "javascript":
            return (
                "var SparseVector = function(nums) {\n"
                "    // Initialize your sparse representation here\n};\n\n"
                "SparseVector.prototype.dotProduct = function(vec) {\n"
                "    // Write your solution here\n};\n"
            )
        if language_id == "cpp":
            return (
                "#include <vector>\nusing namespace std;\n\nclass SparseVector {\npublic:\n"
                "    SparseVector(vector<int> nums) {\n"
                "        // Initialize your sparse representation here\n    }\n\n"
                "    int dotProduct(SparseVector& vec) {\n"
                "        // Write your solution here\n        return 0;\n    }\n};\n"
            )
        if language_id == "java":
            return (
                "class SparseVector {\n"
                "    SparseVector(int[] nums) {\n"
                "        // Initialize your sparse representation here\n    }\n\n"
                "    public int dotProduct(SparseVector vec) {\n"
                "        // Write your solution here\n        return 0;\n    }\n}\n"
            )
        if language_id == "csharp":
            return (
                "public class SparseVector\n{\n"
                "    public SparseVector(int[] nums)\n    {\n"
                "        // Initialize your sparse representation here\n    }\n\n"
                "    public int DotProduct(SparseVector vec)\n    {\n"
                "        // Write your solution here\n        return 0;\n    }\n}\n"
            )
        if language_id == "go":
            return (
                "package main\n\ntype SparseVector struct{}\n\n"
                "func Constructor(nums []int) SparseVector {\n    return SparseVector{}\n}\n\n"
                "func (obj *SparseVector) DotProduct(vec SparseVector) int {\n    return 0\n}\n"
            )
        if language_id == "c":
            return (
                "#include <stddef.h>\n\ntypedef struct SparseVector SparseVector;\n"
                "SparseVector *sparseVectorCreate(const int *nums, size_t numsSize);\n"
                "int sparseVectorDotProduct(SparseVector *obj, SparseVector *vec);\n"
                "void sparseVectorFree(SparseVector *obj);\n"
            )

    raise ValueError(f"Unsupported special starter: {kind}/{language_id}")


def starter_code(problem: dict[str, Any], language_id: str) -> str:
    special = SPECIAL_KIND_BY_ID.get(str(problem["id"]))
    if special:
        return _special_starter(problem, language_id, special)
    if _is_design_problem(problem):
        return _design_starter(problem, language_id)
    return _solution_starter(problem, language_id)
