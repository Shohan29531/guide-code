from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "core" / "imported_problems.json"

DESCRIPTION_OVERRIDES = {
    "Interleaving String": (
        "Given strings `s1`, `s2`, and `s3`, determine whether `s3` can be formed "
        "by interleaving all characters from `s1` and `s2`.\n\n"
        "Characters taken from each source string must keep their original "
        "left-to-right order. The completed interleaving must use every character "
        "from both source strings exactly once.\n\n"
        "Return `true` when `s3` is a valid interleaving. Otherwise, return `false`."
    ),
    "Contains Duplicate II": (
        "Given an integer array `nums` and an integer `k`, determine whether two "
        "different indices contain the same value while being at most `k` positions "
        "apart.\n\nReturn `true` if indices `i` and `j` exist with `i != j`, "
        "`nums[i] == nums[j]`, and `abs(i - j) <= k`. Otherwise, return `false`."
    ),
    "Adjacent Increasing Subarrays Detection I": (
        "Given an integer array `nums` and an integer `k`, look for two adjacent "
        "subarrays that each contain exactly `k` values.\n\n"
        "Both subarrays must be strictly increasing, and the second must begin "
        "immediately after the first ends.\n\nReturn `true` if such a pair exists. "
        "Otherwise, return `false`."
    ),
    "Adjacent Increasing Subarrays Detection II": (
        "Given an integer array `nums`, consider pairs of adjacent subarrays having "
        "the same positive length `k`.\n\nBoth subarrays must be strictly increasing, "
        "and the second must begin immediately after the first ends.\n\n"
        "Return the greatest possible value of `k`."
    ),
    "K-diff Pairs in an Array": (
        "Given an integer array `nums` and a nonnegative integer `k`, count the "
        "distinct value pairs whose absolute difference is exactly `k`.\n\n"
        "A pair must come from two different indices. Equal value pairs count only "
        "once, regardless of how many matching index pairs exist.\n\n"
        "Return the number of unique pairs."
    ),
    "Validate IP Address": (
        "Given a string `queryIP`, classify it as `\"IPv4\"`, `\"IPv6\"`, or "
        "`\"Neither\"`.\n\nA valid IPv4 address has four decimal components separated "
        "by dots. Each component is from `0` through `255`, contains only digits, "
        "and has no leading zero unless the component is exactly `0`.\n\n"
        "A valid IPv6 address has eight components separated by colons. Each "
        "component contains one to four hexadecimal digits; leading zeroes and "
        "uppercase or lowercase letters are allowed."
    ),
    "Time Based Key-Value Store": (
        "Implement a time-based key-value store. `set(key, value, timestamp)` records "
        "a value for a key at that timestamp.\n\n"
        "`get(key, timestamp)` returns the value from the greatest recorded timestamp "
        "that is less than or equal to the requested timestamp, or an empty string "
        "when no such record exists.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Design Twitter": (
        "Implement a simplified social feed. `postTweet(userId, tweetId)` publishes "
        "a new tweet for a user.\n\n`follow(followerId, followeeId)` starts following "
        "another user, and `unfollow(followerId, followeeId)` removes that relationship.\n\n"
        "`getNewsFeed(userId)` returns up to the 10 most recent tweet IDs posted by "
        "the user or by accounts they follow, ordered newest first.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Design Linked List": (
        "Implement a zero-indexed linked list.\n\n"
        "`get(index)` returns the value at an index, or `-1` when the index is invalid. "
        "`addAtHead(value)` and `addAtTail(value)` insert at the corresponding end.\n\n"
        "`addAtIndex(index, value)` inserts before the current node at `index`; an "
        "index equal to the length appends, while an index greater than the length "
        "does nothing. `deleteAtIndex(index)` removes a valid indexed node.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Min Stack": (
        "Implement a stack supporting `push(value)`, `pop()`, and `top()`.\n\n"
        "`getMin()` returns the smallest value currently in the stack. Every `top`, "
        "`pop`, and `getMin` call is made while the stack is nonempty.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Flatten 2D Vector": (
        "Implement an iterator over a list of integer lists. Empty inner lists are "
        "allowed.\n\n`next()` returns the next integer in row-major order. `hasNext()` "
        "returns whether another integer remains.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "LFU Cache": (
        "Implement a fixed-capacity least-frequently-used cache.\n\n"
        "`get(key)` returns the stored value or `-1` when the key is absent. "
        "`put(key, value)` inserts or updates a value. Accessing or updating a key "
        "increases its use count.\n\n"
        "When an insertion exceeds capacity, remove the key with the lowest use "
        "count; if several keys tie, remove the least recently used among them.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Design Hit Counter": (
        "Implement a counter for timestamped hits. Timestamps arrive in chronological "
        "order.\n\n`hit(timestamp)` records one hit. `getHits(timestamp)` returns the "
        "number of hits in the preceding 300 seconds, including the current second "
        "and excluding hits at or before `timestamp - 300`.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Design Tic-Tac-Toe": (
        "Implement an `n × n` tic-tac-toe board. Each `move(row, col, player)` places "
        "that player's mark in an empty cell; all supplied moves are valid.\n\n"
        "Return the player number when the move completes an entire row, column, or "
        "diagonal. Return `0` when nobody has won after the move.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Find K Closest Elements": (
        "Given a sorted integer array `arr`, an integer `k`, and a value `x`, return "
        "the `k` values closest to `x` in ascending order.\n\n"
        "A value with a smaller absolute difference from `x` is closer. When two "
        "values are equally distant, the smaller value is considered closer."
    ),
    "Search in Rotated Sorted Array II": (
        "An integer array was sorted in nondecreasing order and then rotated at an "
        "unknown position. Duplicate values may be present.\n\n"
        "Given the rotated array `nums` and an integer `target`, return `true` if "
        "`target` occurs in the array. Otherwise, return `false`."
    ),
    "Find in Mountain Array": (
        "A mountain array has at least three values, rises strictly to one peak, and "
        "then falls strictly.\n\nGiven `target` and a mountain array, return the "
        "smallest index whose value equals `target`, or `-1` when the target does not "
        "occur.\n\nIn this lab the mountain array is supplied directly as a list."
    ),
    "Word Ladder": (
        "A transformation changes exactly one letter of a word. Every intermediate "
        "word and the final word must occur in `wordList`.\n\n"
        "Given `beginWord`, `endWord`, and `wordList`, return the number of words in "
        "the shortest valid transformation sequence, including both endpoints. "
        "Return `0` when no sequence exists."
    ),
    "Word Ladder II": (
        "A transformation changes exactly one letter of a word. Every intermediate "
        "word and the final word must occur in `wordList`.\n\n"
        "Given `beginWord`, `endWord`, and `wordList`, return every shortest valid "
        "transformation sequence. Each sequence includes both endpoints. Return an "
        "empty list when no sequence exists."
    ),
    "Maximum Sum Circular Subarray": (
        "Given a nonempty circular integer array `nums`, find the greatest sum of a "
        "nonempty contiguous subarray.\n\n"
        "The end of the array connects to its beginning, so a subarray may wrap "
        "around that boundary. No input position may be used more than once.\n\n"
        "Return the greatest possible sum."
    ),
    "Jump Game II": (
        "You begin at index `0` of the nonnegative integer array `nums`. From index "
        "`i`, you may move forward by any distance from `1` through `nums[i]` without "
        "leaving the array.\n\nReturn the minimum number of jumps needed to reach the "
        "last index. Every test case is guaranteed to be reachable."
    ),
    "Last Stone Weight": (
        "Repeatedly choose the two heaviest stones. If their weights are equal, "
        "destroy both. Otherwise, destroy the lighter stone and replace the heavier "
        "one with the difference between their weights.\n\n"
        "Continue until at most one stone remains. Return its weight, or `0` when no "
        "stone remains."
    ),
    "Interval List Intersections": (
        "You are given two lists of closed intervals. Within each list, intervals "
        "are sorted and do not overlap.\n\n"
        "Return every nonempty intersection between an interval from `firstList` and "
        "an interval from `secondList`, in ascending order."
    ),
    "My Calendar I": (
        "Implement a calendar that accepts a booking only when it does not overlap "
        "an existing booking. Each event uses the half-open interval `[start, end)`, "
        "so an event ending exactly when another starts does not overlap.\n\n"
        "`book(start, end)` returns `true` and stores the event when it is valid. It "
        "returns `false` without changing the calendar when a conflict exists.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Minimum Interval to Include Each Query": (
        "Each closed interval `[left, right]` contains every integer from `left` "
        "through `right`, and its size is `right - left + 1`.\n\n"
        "For each value in `queries`, find the size of the smallest input interval "
        "that contains it. Use `-1` when no interval contains the query.\n\n"
        "Return the answers in the same order as the queries."
    ),
    "Friends Of Appropriate Ages": (
        "For every ordered pair of different people `x` and `y`, person `x` sends a "
        "request unless `age[y] <= 0.5 * age[x] + 7`, `age[y] > age[x]`, or "
        "`age[y] > 100` while `age[x] < 100`.\n\n"
        "Requests are directional: a request from `x` to `y` does not imply a "
        "request from `y` to `x`.\n\nReturn the total number of requests."
    ),
    "Sort Integers by The Power Value": (
        "The power of a positive integer is the number of steps needed to reach `1` "
        "by replacing an even value with `x / 2` and an odd value with `3 * x + 1`.\n\n"
        "Sort every integer from `lo` through `hi` by increasing power, breaking ties "
        "by increasing numeric value.\n\nReturn the `k`th value in that ordering, "
        "where `k` is one-based."
    ),
    "Next Greater Element I": (
        "The next greater element of a value is the first strictly larger value to "
        "its right.\n\nThe distinct values in `nums1` all occur in `nums2`. For each "
        "value in `nums1`, find its next greater element in `nums2`, or use `-1` when "
        "none exists.\n\nReturn the answers in `nums1` order."
    ),
    "132 Pattern": (
        "Given an integer array `nums`, determine whether there are indices "
        "`i < j < k` such that `nums[i] < nums[k] < nums[j]`.\n\n"
        "Return `true` if such a subsequence exists. Otherwise, return `false`."
    ),
    "Two Sum II - Input Array Is Sorted": (
        "The integer array `numbers` is sorted in nondecreasing order. Find two "
        "different positions whose values sum to `target`.\n\n"
        "Exactly one solution exists. Return the two one-based indices in increasing "
        "order, and do not use the same position twice."
    ),
    "4Sum": (
        "Given an integer array `nums` and an integer `target`, find every unique "
        "combination of four values from distinct indices whose sum equals `target`.\n\n"
        "Return each quadruplet in nondecreasing order, without duplicate "
        "quadruplets."
    ),
    "Shortest Path to Get All Keys": (
        "The grid contains one start cell `@`, walls `#`, open cells `.`, lowercase "
        "keys, and uppercase locks. You may move one cell up, down, left, or right.\n\n"
        "A lock can be entered only after collecting its matching key. Return the "
        "fewest moves needed to collect every key, or `-1` when that is impossible."
    ),
    "Range Sum Query - Immutable": (
        "Implement an immutable integer array that answers inclusive range-sum "
        "queries.\n\n`sumRange(left, right)` returns the sum of values from index "
        "`left` through index `right`, where `0 <= left <= right < len(nums)`.\n\n"
        "For this lab, `solve(operations, arguments)` receives parallel arrays and "
        "returns one result per operation, using `null` for constructors and methods "
        "that do not return a value."
    ),
    "Minimum Number of Operations to Make All Array Elements Equal to 1": (
        "In one operation, choose adjacent values `nums[i]` and `nums[i + 1]` and "
        "replace either one with their greatest common divisor.\n\n"
        "Return the minimum number of operations needed to make every array value "
        "equal to `1`, or `-1` if it is impossible."
    ),
    "Reverse Linked List II": (
        "Given a singly linked list and one-based positions `left` and `right`, "
        "reverse the nodes from `left` through `right` while leaving all other nodes "
        "in place.\n\nReturn the resulting list. Linked-list inputs and outputs use "
        "plain value arrays in this lab."
    ),
    "Compare Version Numbers": (
        "Version strings contain integer revisions separated by dots. Compare "
        "corresponding revisions from left to right after ignoring leading zeroes. "
        "Missing revisions count as `0`.\n\n"
        "Return `-1` when `version1` is smaller, `1` when it is greater, and `0` when "
        "the two versions are equivalent."
    ),
    "Integer to Roman": (
        "Convert the integer `num` to a Roman numeral. The symbols are `I = 1`, "
        "`V = 5`, `X = 10`, `L = 50`, `C = 100`, `D = 500`, and `M = 1000`.\n\n"
        "Normally symbols appear from larger to smaller values. Use the subtractive "
        "pairs `IV`, `IX`, `XL`, `XC`, `CD`, and `CM` for 4, 9, 40, 90, 400, and "
        "900 respectively.\n\nReturn the canonical Roman numeral for `num`."
    ),
    "Roman to Integer": (
        "Convert the Roman numeral string `s` to an integer. The symbols are "
        "`I = 1`, `V = 5`, `X = 10`, `L = 50`, `C = 100`, `D = 500`, and "
        "`M = 1000`.\n\nThe subtractive pairs `IV`, `IX`, `XL`, `XC`, `CD`, and "
        "`CM` represent 4, 9, 40, 90, 400, and 900. All other symbols contribute "
        "their individual values.\n\nReturn the represented integer."
    ),
}


NO_VISUAL_TITLES = {
    "Add Digits",
    "Binary Number with Alternating Bits",
    "Contains Duplicate II",
    "Count Primes",
    "Detect Capital",
    "Distribute Money to Maximum Children",
    "Divide Two Integers",
    "Excel Sheet Column Number",
    "Excel Sheet Column Title",
    "Factorial Trailing Zeroes",
    "First Missing Positive",
    "Flatten Nested List Iterator",
    "Flatten a Multilevel Doubly Linked List",
    "Greatest Common Divisor of Strings",
    "Happy Number",
    "Integer Break",
    "Integer to English Words",
    "Integer to Roman",
    "Isomorphic Strings",
    "Length of Last Word",
    "Nim Game",
    "Number of 1 Bits",
    "Palindrome Number",
    "Permutations II",
    "Power of Two",
    "Repeated Substring Pattern",
    "Reverse Bits",
    "Reverse Integer",
    "Roman to Integer",
    "Smallest Integer Divisible by K",
    "Sqrt(x)",
    "Sum of Two Integers",
    "Ugly Number",
    "Valid Anagram",
    "Valid Number",
    "Valid Perfect Square",
    "Validate IP Address",
    "Water Bottles",
    "Word Pattern",
    "Serialize and Deserialize N-ary Tree",
    "Burst Balloons",
    "Cherry Pickup",
    "Cherry Pickup II",
    "Number of Longest Increasing Subsequence",
    "Regular Expression Matching",
    "Scramble String",
    "Sum of Subarray Minimums",
    "Tiling a Rectangle with the Fewest Squares",
    "Wildcard Matching",
}

GRID_PARAMETER_NAMES = {
    "board",
    "costs",
    "dungeon",
    "graph",
    "grid",
    "heights",
    "image",
    "mat",
    "matrix",
    "obstaclegrid",
    "room",
    "rooms",
}

INTERVAL_PARAMETER_NAMES = {
    "firstlist",
    "intervals",
}

POINT_TITLES = {
    "K Closest Points to Origin",
    "Max Points on a Line",
    "Min Cost to Connect All Points",
}

DP_STRING_TITLES = {
    "Distinct Subsequences",
    "Edit Distance",
    "Interleaving String",
    "Longest Common Subsequence",
}

TREE_OUTPUT_TITLES = {
    "Construct Binary Tree from Inorder and Postorder Traversal",
    "Construct Binary Tree from Preorder and Inorder Traversal",
    "Convert Sorted Array to Binary Search Tree",
    "Convert Sorted List to Binary Search Tree",
}

TREE_PAIR_TITLES = {
    "Leaf-Similar Trees",
    "Same Tree",
    "Subtree of Another Tree",
}

TREE_COMPARE_TITLES = {
    "Delete Leaves With a Given Value",
    "Invert Binary Tree",
    "Recover Binary Search Tree",
}

TREE_FOREST_TITLES = {
    "Delete Nodes And Return Forest",
    "Find Duplicate Subtrees",
}

TREE_LIST_TITLES = {
    "Convert Binary Search Tree to Sorted Doubly Linked List",
    "Flatten Binary Tree to Linked List",
}

TREE_NODE_RESULT_TITLES = {
    "Closest Binary Search Tree Value",
    "Inorder Successor in BST",
    "Inorder Successor in BST II",
    "Kth Smallest Element in a BST",
    "Lowest Common Ancestor of a Binary Search Tree",
    "Lowest Common Ancestor of a Binary Tree",
    "Lowest Common Ancestor of a Binary Tree II",
    "Lowest Common Ancestor of a Binary Tree III",
}

TREE_TRAVERSAL_TITLES = {
    "Binary Tree Inorder Traversal",
    "Binary Tree Postorder Traversal",
    "Binary Tree Preorder Traversal",
    "Boundary of Binary Tree",
}

GRID_COMPARE_TITLES = {
    "Sudoku Solver",
    "Walls and Gates",
}

DP_GRID_TITLES = {
    "Dungeon Game": "dungeon_dp",
    "Longest Increasing Path in a Matrix": "matrix_path",
    "Maximal Rectangle": "matrix_region",
    "Maximal Square": "matrix_region",
    "Minimum Falling Path Sum": "matrix_path",
    "Minimum Path Sum": "matrix_path",
    "Paint House": "paint_house",
    "Paint House II": "paint_house",
    "Triangle": "triangle_path",
    "Unique Paths": "path_count_grid",
    "Unique Paths II": "path_count_grid",
}

STRING_VISUAL_WORDS = {
    "Abbreviation",
    "Calculator",
    "Compression",
    "Decode",
    "Echo",
    "Expansion",
    "File Path",
    "Genetic",
    "Happy Prefix",
    "Interleaving",
    "Palindrome",
    "Parentheses",
    "Partition",
    "Pattern",
    "Prefix",
    "Remove",
    "Repeated",
    "Reverse",
    "Strobogrammatic",
    "Substring",
    "Version",
    "Vowels",
    "Window",
    "Zigzag",
}

SEQUENCE_VISUAL_WORDS = {
    "132 Pattern",
    "Array",
    "Asteroid",
    "Balloons",
    "Candy",
    "Consecutive",
    "Contiguous",
    "Distance",
    "Flower",
    "Gap",
    "Gas Station",
    "Hand of Straights",
    "H-Index",
    "Jump Game",
    "Mountain",
    "Next Greater",
    "Next Permutation",
    "Peak",
    "Permutation",
    "Pivot",
    "Prefix Sum",
    "Range",
    "Ribbons",
    "Robber",
    "Seats",
    "Shipping",
    "Single Element",
    "Sort",
    "Subarray",
    "Subsequence",
    "Task Scheduler",
    "Three Numbers",
    "Two Sum II",
}

BAR_VISUAL_WORDS = {
    "Histogram",
    "Ocean View",
    "Stock",
    "Temperature",
    "Trapping Rain Water",
}

TRANSFORMATION_TITLES = {
    "Add to Array-Form of Integer",
    "Diagonal Traverse",
    "Diagonal Traverse II",
    "Find All Numbers Disappeared in an Array",
    "Flatten Binary Tree to Linked List",
    "Merge Sorted Array",
    "Next Permutation",
    "Remove Element",
    "Rotate Array",
    "Rotate Image",
    "Sort Colors",
    "Sort Even and Odd Indices Independently",
    "Sort Matrix by Diagonals",
    "Sparse Matrix Multiplication",
    "Squares of a Sorted Array",
    "String Compression",
    "Surrounded Regions",
    "Transpose Matrix",
}


def parameter_names(problem: dict[str, Any]) -> list[str]:
    tree = ast.parse(f"{problem['signature']}\n    pass\n")
    function = tree.body[0]
    return [argument.arg for argument in function.args.args]


def json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def formatted_input(problem: dict[str, Any], args: list[Any]) -> str:
    pieces = [
        f"{name} = {json_value(value)}"
        for name, value in zip(parameter_names(problem), args)
    ]
    one_line = ", ".join(pieces)
    return one_line if len(one_line) <= 110 else ",\n".join(pieces)


def compact_summary(text: str) -> str:
    clean = re.sub(r"[`*_#]", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", clean)[0]
    if len(first_sentence) <= 92:
        return first_sentence
    shortened = first_sentence[:89].rsplit(" ", 1)[0].rstrip(",:;")
    return shortened + "…"


GENERIC_EXPLANATION_MARKERS = (
    "Applying the problem rules",
    "These are the values produced",
    "At least one required condition fails",
    "Evaluating the stated requirement",
    "The best valid region for this input",
)

FALSE_EXPLANATIONS = {
    "Adjacent Increasing Subarrays Detection I": "No adjacent pair of length-`k` subarrays is strictly increasing.",
    "Balanced Binary Tree": "At least one node's two subtree heights differ by more than one.",
    "Can Place Flowers": "The available nonadjacent plots cannot hold all requested flowers.",
    "Car Pooling": "The overlapping trips require more seats than the car's capacity.",
    "Contains Duplicate II": "No equal values occur within `k` positions of each other.",
    "Continuous Subarray Sum": "No qualifying contiguous subarray has a sum divisible by `k`.",
    "Detect Capital": "The word's uppercase and lowercase pattern is not one of the allowed forms.",
    "Happy Number": "The digit-square sequence enters a cycle without reaching `1`.",
    "Is Subsequence": "The characters of `s` cannot all be matched in order inside `t`.",
    "Leaf-Similar Trees": "The two trees produce different left-to-right leaf sequences.",
    "Palindrome Linked List": "The node values differ when read from opposite ends.",
    "Partition to K Equal Sum Subsets": "The values cannot be split into `k` groups with equal sums.",
    "Permutation in String": "No window in `s2` has the same character counts as `s1`.",
    "Power of Two": "The value is not an exact integer power of two.",
    "Repeated Substring Pattern": "No shorter substring can be repeated to form the entire input.",
    "Rotate String": "No rotation of `s` matches `goal`.",
    "Same Tree": "The two trees differ in structure or in at least one node value.",
    "Scramble String": "No valid recursive partition and swap sequence transforms one string into the other.",
    "Search a 2D Matrix": "The target does not occur in the matrix.",
    "Search a 2D Matrix II": "The target does not occur in the matrix.",
    "Search in Rotated Sorted Array II": "The target does not occur in the rotated array.",
    "Subtree of Another Tree": "No node in the first tree roots a tree identical to `subRoot`.",
    "Symmetric Tree": "The left and right sides fail the required mirror comparison.",
    "Valid Number": "The string does not match the permitted numeric syntax.",
    "Valid Palindrome II": "More than one deletion would be needed to form a palindrome.",
    "Word Pattern": "The words and pattern letters do not form a one-to-one mapping.",
    "Word Search": "No adjacent-cell path spells the complete word.",
}


def specific_explanation(
    problem: dict[str, Any],
    expected: Any,
    original: str,
) -> str:
    if not any(marker in original for marker in GENERIC_EXPLANATION_MARKERS):
        return original

    title = problem["title"]
    lower = title.lower()
    shown = json_value(expected)

    if isinstance(expected, bool):
        if expected:
            return "Every required condition holds for this input, so the result is `true`."
        return FALSE_EXPLANATIONS.get(
            title,
            "At least one required condition fails for this input, so the result is `false`.",
        )

    if isinstance(expected, list):
        if not expected:
            return "No value satisfies the required conditions, so the result is an empty list."
        if all(isinstance(item, list) for item in expected):
            noun = "groups"
            if "interval" in lower:
                noun = "intervals"
            elif "path" in lower or "ladder" in lower:
                noun = "paths"
            elif "sum" in lower or "combination" in lower:
                noun = "combinations"
            elif "matrix" in lower or "triangle" in lower:
                noun = "rows"
            return (
                f"The output contains {len(expected)} valid {noun}, with each one "
                "ordered according to the statement."
            )
        return (
            f"The result contains {len(expected)} value"
            f"{'s' if len(expected) != 1 else ''} in the required order: `{shown}`."
        )

    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if title == "Rectangle Area":
            return f"After accounting for their overlap, the rectangles cover `{shown}` square units."
        if title == "Maximal Square":
            return f"The largest all-`1` square has area `{shown}`."
        if title in {"Unique Paths", "Unique Paths II"}:
            return f"Exactly `{shown}` valid right-and-down routes reach the destination."
        if title in {"Coin Change II", "Combination Sum IV", "Target Sum"}:
            return f"Exactly `{shown}` valid combinations produce the requested total."
        if title in {"N-Queens II", "Unique Binary Search Trees"}:
            return f"Exactly `{shown}` distinct valid structures can be formed."
        if title == "Filling Bookcase Shelves":
            return f"The shortest possible completed bookcase has total height `{shown}`."
        if title == "House Robber II":
            return f"The best nonadjacent selection around the circle contains `{shown}` total money."
        if title == "Triangle":
            return f"The smallest top-to-bottom path sum is `{shown}`."
        if title == "Burst Balloons":
            return f"The best valid bursting order earns `{shown}` coins."
        if title == "Cherry Pickup":
            return f"The two routes can collect at most `{shown}` cherries."
        if title == "Repeated String Match":
            return f"`a` must be repeated `{shown}` times before it can contain `b`."
        if title == "Russian Doll Envelopes":
            return f"At most `{shown}` envelopes can be nested with both dimensions increasing."
        if title == "Course Schedule III":
            return f"At most `{shown}` courses can be completed before their deadlines."
        if title == "Subarray Sum Equals K":
            return f"Exactly `{shown}` contiguous subarrays sum to `k`."
        if title == "Subarray Product Less Than K":
            return f"Exactly `{shown}` contiguous subarrays have product below `k`."
        if title == "Path Sum III":
            return f"Exactly `{shown}` downward tree paths have the target sum."
        if title == "Sum of Nodes with Even-Valued Grandparent":
            return f"The qualifying node values add up to `{shown}`."
        if title == "Palindrome Partitioning II":
            return f"The string can be partitioned into palindromes with `{shown}` cuts, and no fewer."
        if "kth" in lower or title.startswith("Kth"):
            return f"The value at the requested rank is `{shown}`."
        if title == "Search Insert Position":
            return f"The target belongs at index `{shown}` while preserving sorted order."
        if any(
            phrase in lower
            for phrase in (
                "single element",
                "single number",
                "find the duplicate",
            )
        ):
            return f"The value singled out by the stated condition is `{shown}`."
        if title == "Island Perimeter":
            return f"The exposed edges around the island total `{shown}` units."
        if any(phrase in lower for phrase in ("rotting oranges", "network delay")):
            return f"All reachable nodes are covered after `{shown}` time units."
        if any(phrase in lower for phrase in ("snakes and ladders", "jump game ii")):
            return f"The destination can be reached in no fewer than `{shown}` moves."
        if title == "Last Stone Weight":
            return f"After every smash, the remaining stone weighs `{shown}`."
        if "angle between hands" in lower:
            return f"The smaller angle between the clock hands is `{shown}` degrees."
        if "diameter" in lower:
            return f"The longest path between two nodes uses `{shown}` edges."
        if "lowest common ancestor" in lower:
            return f"The lowest node containing both targets in its subtree has value `{shown}`."
        if title == "Trapping Rain Water":
            return f"The bars hold `{shown}` total units of water."
        if title == "Factorial Trailing Zeroes":
            return f"The factorial ends with exactly `{shown}` zeroes."
        if title == "Dungeon Game":
            return f"The knight needs at least `{shown}` initial health to survive."
        if any(
            phrase in lower
            for phrase in (
                "calculator",
                "sum of two integers",
                "pow(",
                "reverse integer",
                "add digits",
                "excel sheet column number",
                "bitwise and",
            )
        ):
            return f"The expression or conversion evaluates to `{shown}`."
        if any(word in lower for word in ("minimum", "min ", "shortest", "least")):
            return f"No valid result is smaller than `{shown}` for this input."
        if any(
            word in lower
            for word in ("maximum", "maximize", "max ", "longest", "largest")
        ):
            return (
                f"`{shown}` is achievable for this input, and no valid result is larger."
            )
        if any(
            word in lower
            for word in ("count", "number of", "ways", "combination")
        ):
            return f"Exactly `{shown}` valid outcomes satisfy the requirements."
        if "index" in lower or "occurrence" in lower:
            return f"The required matching position is index `{shown}`."
        if "area" in lower or "rectangle" in lower:
            return f"The best valid region for this input has area `{shown}`."
        if "profit" in lower or "stock" in lower:
            return f"The best permitted transactions produce a profit of `{shown}`."
        if "depth" in lower:
            return f"The first example spans `{shown}` tree levels."
        return f"Evaluating the stated requirement for this input gives `{shown}`."

    if isinstance(expected, str):
        if not expected:
            return "No nonempty result satisfies the requirements, so the output is an empty string."
        return f"The required text for this input is `{shown}`."

    return f"The required result for this input is `{shown}`."


def styled_description(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    result: list[str] = []
    for paragraph in paragraphs:
        if paragraph.startswith("- ") or len(paragraph) <= 330:
            result.append(paragraph)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        chunk: list[str] = []
        size = 0
        for sentence in sentences:
            if chunk and size + len(sentence) > 300:
                result.append(" ".join(chunk))
                chunk = []
                size = 0
            chunk.append(sentence)
            size += len(sentence)
        if chunk:
            result.append(" ".join(chunk))
    if len(result) > 8 or sum(map(len, result)) > 1050:
        essential: list[str] = []
        for paragraph in result:
            lower = paragraph.lower()
            if len(essential) < 4 or any(
                marker in lower
                for marker in (
                    "return ",
                    "for this lab",
                    "in this lab",
                    "instead of",
                    "the output",
                )
            ):
                if paragraph not in essential:
                    essential.append(paragraph)
            if len(essential) == 8:
                break
        result = essential
    return "\n\n".join(result)


def is_rectangular_grid(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(row, list) and bool(row) for row in value)
        and len({len(row) for row in value}) == 1
        and len(value) <= 10
        and len(value[0]) <= 16
        and all(
            isinstance(cell, (int, float, str, bool)) or cell is None
            for row in value
            for cell in row
        )
    )


def find_parameter_index(names: list[str], candidates: set[str]) -> int | None:
    for index, name in enumerate(names):
        if name in candidates:
            return index
    return None


def visualization_decision(problem: dict[str, Any]) -> dict[str, Any] | None:
    title = problem["title"]
    if title in NO_VISUAL_TITLES:
        return None

    names = parameter_names(problem)
    first_test = problem["tests"][0]
    args = first_test["args"]
    expected = first_test["expected"]
    tags = set(problem["tags"])

    if names == ["operations", "arguments"]:
        return {"kind": "operations"}

    if title == "Rectangle Area":
        return {"kind": "rectangles"}
    if title == "Angle Between Hands of a Clock":
        return {"kind": "clock"}
    if title in {"Pascal's Triangle", "Pascal's Triangle II"}:
        return {"kind": "pyramid"}
    if title in {"N-Queens", "N-Queens II"}:
        return {"kind": "queens"}
    if title == "Find the Duplicate Number":
        return {"kind": "sequence_auto", "arg_index": 0}
    if title == "Maximum Product Subarray":
        return {"kind": "subarray_result", "arg_index": 0}
    if title == "House Robber II":
        return {"kind": "house_circle", "arg_index": 0}
    if title in {"Jump Game", "Jump Game II"}:
        return {"kind": "jump_path", "arg_index": 0}
    if title == "Split Array Largest Sum":
        return {"kind": "split_array", "arg_index": 0}
    if title == "Palindrome Partitioning II":
        return {"kind": "pal_partition", "arg_index": 0}
    if title == "Intersection of Two Linked Lists":
        return {
            "kind": "linked_list",
            "arg_indexes": [1, 2],
            "grouped": True,
        }
    if title == "Min Cost Climbing Stairs":
        return {"kind": "stair_costs", "arg_index": 0}
    if title == "Best Time to Buy and Sell Stock IV":
        return {"kind": "bars_auto", "arg_index": 1}
    if title == "Maximum Profit from Trading Stocks":
        return {"kind": "paired_bars", "arg_indexes": [0, 1]}
    if title in DP_GRID_TITLES:
        decision = {"kind": DP_GRID_TITLES[title]}
        grid_index = find_parameter_index(names, GRID_PARAMETER_NAMES)
        if grid_index is not None:
            decision["arg_index"] = grid_index
        return decision
    if title == "Knight Dialer":
        return {"kind": "keypad"}
    if title == "Filling Bookcase Shelves":
        return {"kind": "books", "arg_index": 0}
    if title == "Count Unguarded Cells in the Grid":
        return {"kind": "guard_grid"}
    if title == "Minimum Knight Moves":
        return {"kind": "knight"}
    if title == "Car Pooling":
        return {"kind": "trips", "arg_index": 0}
    if title == "The Skyline Problem":
        return {"kind": "buildings", "arg_index": 0}
    if title == "Car Fleet":
        return {"kind": "fleet"}
    if title == "Find Winner on a Tic Tac Toe Game":
        return {"kind": "tic_tac_toe", "arg_index": 0}
    if title == "Snakes and Ladders":
        return {"kind": "snakes_board", "arg_index": 0}
    if title == "Shortest Path to Get All Keys":
        return {"kind": "character_grid", "arg_index": 0}
    if title == "Dot Product of Two Sparse Vectors":
        return {"kind": "paired_bars", "arg_indexes": [0, 1]}
    if title == "Sparse Matrix Multiplication":
        return {"kind": "matrix_pair", "arg_indexes": [0, 1]}
    if title == "The Earliest Moment When Everyone Become Friends":
        return {"kind": "timestamp_graph", "arg_index": 0}

    if title in POINT_TITLES:
        return {"kind": "points", "arg_index": 0}

    interval_index = find_parameter_index(names, INTERVAL_PARAMETER_NAMES)
    if interval_index is not None and interval_index < len(args):
        intervals = args[interval_index]
        if (
            isinstance(intervals, list)
            and intervals
            and all(
                isinstance(item, list)
                and len(item) >= 2
                and all(isinstance(value, (int, float)) for value in item[:2])
                for item in intervals
            )
        ):
            return {"kind": "intervals_auto", "arg_index": interval_index}

    tree_like = (
        "Tree" in tags
        or "Trees" in tags
        or "Binary Tree" in title
        or "BST" in title
    )
    if tree_like and args and isinstance(args[0], list):
        if title in TREE_OUTPUT_TITLES:
            return {"kind": "tree", "source": "expected"}
        if title in TREE_PAIR_TITLES and len(args) > 1 and isinstance(args[1], list):
            return {"kind": "tree_pair", "arg_indexes": [0, 1]}
        if title == "Merge Two Binary Trees":
            return {"kind": "tree_merge", "arg_indexes": [0, 1]}
        if title in TREE_COMPARE_TITLES:
            return {"kind": "tree_compare", "arg_index": 0}
        if title in TREE_FOREST_TITLES:
            return {"kind": "tree_forest", "arg_index": 0}
        if title in TREE_LIST_TITLES:
            return {"kind": "tree_list", "arg_index": 0}
        decision: dict[str, Any] = {"kind": "tree", "arg_index": 0}
        if title in TREE_NODE_RESULT_TITLES:
            decision["highlight_result"] = True
        if title in TREE_TRAVERSAL_TITLES:
            decision["visit_order"] = True
        if title.startswith("Lowest Common Ancestor") and len(args) >= 3:
            decision["target_arg_indexes"] = [1, 2]
        if title == "All Nodes Distance K in Binary Tree":
            decision["highlight_result_list"] = True
            decision["target_arg_indexes"] = [1]
        if title == "Binary Tree Right Side View":
            decision["highlight_result_list"] = True
        if title == "Range Sum of BST":
            decision["range_arg_indexes"] = [1, 2]
        if title == "Path Sum II":
            decision["highlight_first_path"] = True
        if title in {
            "Populating Next Right Pointers in Each Node",
            "Populating Next Right Pointers in Each Node II",
        }:
            decision["next_links"] = True
        return decision

    linked_like = "Linked List" in tags or any(
        name in {"head", "l1", "l2", "list1", "list2"} for name in names
    )
    if linked_like and args and isinstance(args[0], list):
        return {
            "kind": "linked_list",
            "arg_index": 0,
            "all_list_args": sum(isinstance(value, list) for value in args) > 1,
        }

    graph_index = find_parameter_index(
        names,
        {
            "connections",
            "edges",
            "equations",
            "flights",
            "prerequisites",
            "tickets",
            "times",
        },
    )
    if graph_index is not None and graph_index < len(args):
        edges = args[graph_index]
        if (
            isinstance(edges, list)
            and edges
            and all(isinstance(edge, list) and len(edge) >= 2 for edge in edges)
            and len(edges) <= 24
        ):
            decision = {"kind": "graph_auto", "arg_index": graph_index}
            if title == "Clone Graph":
                decision["adjacency_list"] = True
            if title in {"Course Schedule II"}:
                decision["reverse_edges"] = True
            if title == "Evaluate Division":
                decision["weight_arg_index"] = 1
            if title == "Minimum Time to Collect All Apples in a Tree":
                decision["active_node_arg_index"] = 2
            if title == "Maximum Path Quality of a Graph":
                decision["node_value_arg_index"] = 0
            if names and names[0] in {"n", "numcourses", "num_courses"}:
                decision["node_count_arg_index"] = 0
            return decision

    grid_index = find_parameter_index(names, GRID_PARAMETER_NAMES)
    if grid_index is not None and grid_index < len(args):
        grid = args[grid_index]
        if is_rectangular_grid(grid):
            compare = (
                title in TRANSFORMATION_TITLES | GRID_COMPARE_TITLES
                and is_rectangular_grid(expected)
                and len(grid) == len(expected)
                and len(grid[0]) == len(expected[0])
            )
            return {
                "kind": "grid_compare_auto" if compare else "grid_auto",
                "arg_index": grid_index,
            }

    if title in DP_STRING_TITLES and len(args) >= 2:
        if isinstance(args[0], str) and isinstance(args[1], str):
            return {"kind": "dp_table", "arg_indexes": [0, 1]}

    if args and isinstance(args[0], str):
        if any(word in title for word in STRING_VISUAL_WORDS):
            if 1 <= len(args[0]) <= 28:
                return {"kind": "string_sequence", "arg_index": 0}
        return None

    if args and isinstance(args[0], list) and args[0]:
        sequence = args[0]
        if (
            len(sequence) <= 24
            and all(isinstance(item, (int, float, str, bool)) for item in sequence)
        ):
            if any(word in title for word in BAR_VISUAL_WORDS):
                return {"kind": "bars_auto", "arg_index": 0}
            if (
                title in TRANSFORMATION_TITLES
                and isinstance(expected, list)
                and len(expected) <= 24
            ):
                return {"kind": "sequence_compare", "arg_index": 0}
            if any(word in title for word in SEQUENCE_VISUAL_WORDS):
                return {"kind": "sequence_auto", "arg_index": 0}

    if (
        title == "Spiral Matrix II"
        and is_rectangular_grid(expected)
    ):
        return {"kind": "grid_output"}

    return None


catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
for problem in catalog:
    if problem["title"] == "Design Linked List":
        problem["tests"][0] = {
            "args": [
                [
                    "MyLinkedList",
                    "addAtHead",
                    "addAtTail",
                    "addAtIndex",
                    "get",
                    "deleteAtIndex",
                    "get",
                ],
                [[], [1], [3], [1, 2], [1], [1], [1]],
            ],
            "expected": [None, None, None, None, 2, None, 3],
        }
    problem["summary"] = compact_summary(problem["summary"])
    problem["description"] = styled_description(
        DESCRIPTION_OVERRIDES.get(problem["title"], problem["description"])
    )
    problem["tags"] = problem["tags"][:3]
    for index, example in enumerate(problem["examples"]):
        if index < len(problem["tests"]):
            example["input"] = formatted_input(
                problem,
                list(problem["tests"][index]["args"]),
            )
            example["output"] = json_value(problem["tests"][index]["expected"])
        explanation = re.sub(r"\s+", " ", example["explanation"]).strip()
        if index < len(problem["tests"]):
            explanation = specific_explanation(
                problem,
                problem["tests"][index]["expected"],
                explanation,
            )
        if len(explanation) > 260:
            explanation = explanation[:257].rsplit(" ", 1)[0].rstrip() + "…"
        example["explanation"] = explanation
    problem["visualization"] = visualization_decision(problem)

CATALOG_PATH.write_text(
    json.dumps(catalog, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

visualized = [problem for problem in catalog if problem["visualization"]]
print(
    json.dumps(
        {
            "problems_reviewed": len(catalog),
            "visualized": len(visualized),
            "intentionally_text_only": len(catalog) - len(visualized),
            "visual_kinds": {
                kind: sum(
                    problem["visualization"]["kind"] == kind
                    for problem in visualized
                )
                for kind in sorted(
                    {problem["visualization"]["kind"] for problem in visualized}
                )
            },
        },
        indent=2,
    )
)
