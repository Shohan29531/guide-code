from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _paragraphs(*parts: str) -> str:
    return "\n\n".join(parts)


# Learner-facing statements describe the contract only. Strategy belongs in the
# folded tutor prompts, where learners can choose when to reveal it.
LEARNER_DESCRIPTIONS = {
    "two-sum": _paragraphs(
        "Given an integer list `nums` and an integer `target`, find two different positions whose values add up to `target`.",
        "Exactly one valid pair exists. The same position cannot be used twice, even when the two required values are equal.",
        "Return the two zero-based indices in increasing order.",
    ),
    "valid-parentheses": _paragraphs(
        "You are given a string containing only `(`, `)`, `[`, `]`, `{`, and `}`.",
        "The string is valid when every opening bracket is closed by the same bracket type and the pairs are closed in the correct order.",
        "Return `True` when the entire string is valid. Otherwise, return `False`.",
    ),
    "best-stock-profit": _paragraphs(
        "The value at each position in `prices` is the stock price on that day.",
        "Choose at most one day to buy and one later day to sell. A sale cannot happen before the purchase.",
        "Return the greatest profit possible. If no transaction produces a positive profit, return `0`.",
    ),
    "binary-search": _paragraphs(
        "You are given an ascending list of distinct integers `nums` and an integer `target`.",
        "If `target` appears in the list, return its zero-based index.",
        "If it does not appear, return `-1`.",
    ),
    "contains-duplicate": _paragraphs(
        "You are given an integer list `nums`.",
        "Determine whether any value occurs at more than one position in the list.",
        "Return `True` if a duplicate exists. Otherwise, return `False`.",
    ),
    "valid-anagram": _paragraphs(
        "Two strings are anagrams when the characters of one can be rearranged to form the other.",
        "Every character occurrence matters: repeated characters must appear the same number of times in both strings.",
        "Return `True` if `s` and `t` are anagrams. Otherwise, return `False`.",
    ),
    "merge-sorted-arrays": _paragraphs(
        "The integer lists `a` and `b` are each sorted in nondecreasing order.",
        "Create a new list containing every value from both inputs. Duplicate values must be preserved.",
        "Return the combined values in nondecreasing order.",
    ),
    "move-zeroes": _paragraphs(
        "Given an integer list `nums`, place all zero values after all nonzero values.",
        "The relative order of the nonzero values must stay the same, and no values may be added or removed.",
        "Return the transformed list.",
    ),
    "maximum-subarray": _paragraphs(
        "A subarray is a nonempty sequence of consecutive values from a list.",
        "Given `nums`, consider every possible subarray, including subarrays containing a single value.",
        "Return the largest sum among them.",
    ),
    "majority-element": _paragraphs(
        "The majority element of `nums` is the value that appears more than `len(nums) // 2` times.",
        "The input is nonempty, and a majority element is guaranteed to exist.",
        "Return that value.",
    ),
    "first-unique-character": _paragraphs(
        "A unique character is one that appears exactly once in the entire string `s`.",
        "Find the unique character that occurs earliest in the original string.",
        "Return its zero-based index, or `-1` if no unique character exists.",
    ),
    "ransom-note": _paragraphs(
        "You are given two strings: `note` and `magazine`.",
        "The note can be formed only if the magazine contains every required character occurrence. Each character in `magazine` may be used at most once.",
        "Return `True` if the note can be formed. Otherwise, return `False`.",
    ),
    "valid-palindrome": _paragraphs(
        "Ignore every character in `s` that is not a letter or digit, and treat uppercase and lowercase letters as equal.",
        "The remaining characters form a palindrome when they read the same from left to right and right to left. An empty remaining string counts as a palindrome.",
        "Return `True` if the normalized string is a palindrome. Otherwise, return `False`.",
    ),
    "reverse-words": _paragraphs(
        "A word is a maximal sequence of non-space characters.",
        "Return the words from `s` in reverse order. Do not reverse the characters inside a word.",
        "Separate adjacent output words with one space, with no leading or trailing spaces.",
    ),
    "missing-number": _paragraphs(
        "The list `nums` contains `n` distinct values selected from the inclusive range `0` through `n`.",
        "Exactly one value from that range is missing. The input is not guaranteed to be sorted.",
        "Return the missing value.",
    ),
    "intersection-unique": _paragraphs(
        "Given integer lists `a` and `b`, identify the values that occur in both lists.",
        "Each shared value must appear exactly once in the result, regardless of how often it appears in either input.",
        "Return the shared values in ascending order.",
    ),
    "single-number": _paragraphs(
        "Every value in `nums` appears exactly twice except for one value, which appears once.",
        "The list may contain positive, zero, or negative integers.",
        "Return the value that appears once.",
    ),
    "climbing-stairs": _paragraphs(
        "A staircase has `n` steps, and you begin below the first step.",
        "On each move, you may climb either one step or two steps. Two sequences count as different when their move order differs.",
        "Return the number of distinct sequences that land exactly on step `n`.",
    ),
    "flood-fill": _paragraphs(
        "Each cell in `image` contains an integer color. The starting cell is at row `sr` and column `sc`.",
        "Change the starting cell and every cell connected to it by up, down, left, or right moves that has the same original color. Diagonal contact does not connect cells.",
        "Return the resulting image using `color` as the replacement color.",
    ),
    "counting-bits": _paragraphs(
        "For a nonnegative integer `i`, its bit count is the number of `1` digits in its binary representation.",
        "Given `n`, find the bit count of every integer from `0` through `n`, inclusive.",
        "Return the counts in a list where the value at index `i` is the bit count of `i`.",
    ),
    "longest-unique-substring": _paragraphs(
        "A substring is a sequence of consecutive characters from a string.",
        "Given `s`, find the greatest length of any substring in which no character appears more than once.",
        "Return that length, not the substring itself.",
    ),
    "product-except-self": _paragraphs(
        "For every index `i` in `nums`, calculate the product of all input values except `nums[i]`.",
        "Do not use division. The input may contain zero or negative values.",
        "Return a list whose value at each index is the corresponding product.",
    ),
    "group-anagrams": _paragraphs(
        "Group the strings in `words` so that two strings share a group exactly when one can be rearranged to form the other.",
        "Keep words in their original order inside each group. Order the groups by the first input position represented in each group.",
        "Return the ordered list of groups.",
    ),
    "top-k-frequent": _paragraphs(
        "Given an integer list `nums` and an integer `k`, select the `k` distinct values with the highest occurrence counts.",
        "Order selected values from highest frequency to lowest frequency. When two values have the same frequency, place the smaller value first.",
        "Return the ordered list of selected values.",
    ),
    "three-sum": _paragraphs(
        "Find every set of three values from distinct positions in `nums` whose sum is `0`.",
        "The result must not contain duplicate triplets. Within each triplet, values must appear in nondecreasing order.",
        "Return the triplets in lexicographic order.",
    ),
    "container-most-water": _paragraphs(
        "Each value in `height` represents the height of a vertical line at that index. All lines stand on the same horizontal baseline.",
        "Choose two different lines. Together with the baseline, they contain an area whose width is the distance between their indices and whose height is limited by the shorter line.",
        "Return the greatest area obtainable from any pair.",
    ),
    "minimum-size-subarray-sum": _paragraphs(
        "The list `nums` contains positive integers, and `target` is a positive integer.",
        "Find a nonempty subarray whose sum is at least `target` and whose length is as small as possible.",
        "Return that minimum length, or `0` if no qualifying subarray exists.",
    ),
    "character-replacement": _paragraphs(
        "You may replace at most `k` characters in the uppercase string `s` with any uppercase English letters.",
        "After those replacements, consider substrings made entirely of one repeated character.",
        "Return the greatest possible length of such a substring.",
    ),
    "daily-temperatures": _paragraphs(
        "The value at each index in `temperatures` is the temperature recorded on that day.",
        "For each day, determine how many days must pass before a strictly warmer temperature occurs.",
        "Return a list of those waits. Use `0` for a day that has no warmer future day.",
    ),
    "evaluate-rpn": _paragraphs(
        "`tokens` is a valid arithmetic expression in Reverse Polish notation. Each token is an integer or one of `+`, `-`, `*`, and `/`.",
        "Operators apply to the two preceding expression values. Division of integers truncates toward zero.",
        "Evaluate the complete expression and return its integer result.",
    ),
    "search-rotated-array": _paragraphs(
        "`nums` originally contained distinct integers in ascending order, then may have been rotated at an unknown position.",
        "Given `target`, determine whether and where it appears in the rotated list.",
        "Return its zero-based index, or `-1` when it is absent.",
    ),
    "first-last-position": _paragraphs(
        "The integer list `nums` is sorted in nondecreasing order and may contain repeated values.",
        "Find the first and last positions occupied by `target`.",
        "Return `[first, last]`, or `[-1, -1]` if `target` does not occur.",
    ),
    "koko-bananas": _paragraphs(
        "Each value in `piles` is the number of bananas in one pile. Koko chooses one positive integer eating speed, measured in bananas per hour.",
        "During an hour, she eats up to that speed from one pile. If a pile has fewer bananas, she finishes it and does not begin another pile during the same hour.",
        "Return the smallest speed that lets her finish every pile within `h` hours.",
    ),
    "merge-intervals": _paragraphs(
        "Each pair `[start, end]` in `intervals` represents a closed interval.",
        "Combine all intervals that overlap. Because the intervals are closed, sharing an endpoint counts as overlap.",
        "Return the non-overlapping combined intervals in ascending order by start.",
    ),
    "insert-interval": _paragraphs(
        "`intervals` contains closed intervals sorted by start, and no two existing intervals overlap.",
        "Insert `new_interval`, combining it with every interval it overlaps. Closed intervals that share an endpoint must also be combined.",
        "Return the resulting non-overlapping intervals in ascending order by start.",
    ),
    "spiral-matrix": _paragraphs(
        "Given a rectangular matrix, begin at its top-left cell and read the outer boundary clockwise.",
        "Continue inward, layer by layer, until every cell has been read exactly once.",
        "Return the values in the order they are visited.",
    ),
    "rotate-matrix": _paragraphs(
        "You are given an `n × n` matrix.",
        "Imagine rotating the matrix by `90` degrees clockwise so that rows and columns move to their new positions.",
        "Return a new matrix containing the rotated values.",
    ),
    "set-matrix-zeroes": _paragraphs(
        "Inspect the original values in `matrix`.",
        "If a cell originally contains `0`, every cell in that cell's row and every cell in that cell's column must become `0`.",
        "Return the transformed matrix. Newly written zeroes must not cause additional rows or columns to change.",
    ),
    "number-of-islands": _paragraphs(
        "The grid contains `'1'` for land and `'0'` for water.",
        "An island is a group of land cells connected through up, down, left, or right moves. Diagonal contact does not connect land.",
        "Return the number of separate islands in the grid.",
    ),
    "course-schedule": _paragraphs(
        "There are `num_courses` courses labeled from `0` through `num_courses - 1`.",
        "Each pair `[course, prerequisite]` means the prerequisite must be completed before that course. A course cannot be completed when its requirements form a dependency cycle.",
        "Return `True` if every course can be completed. Otherwise, return `False`.",
    ),
    "shortest-unweighted-path": _paragraphs(
        "The graph has nodes `0` through `n - 1` and undirected edges. Every edge represents one step.",
        "Find the minimum number of edges needed to travel from `start` to `end`.",
        "Return that distance, or `-1` if no path connects the two nodes.",
    ),
    "coin-change": _paragraphs(
        "Each value in `coins` is a positive coin denomination, and any denomination may be used any number of times.",
        "Choose coins whose values add up exactly to `amount`.",
        "Return the fewest coins needed, or `-1` if the amount cannot be formed. An amount of `0` requires `0` coins.",
    ),
    "house-robber": _paragraphs(
        "Each value in `nums` is the amount available at one house along a street.",
        "You may choose any collection of houses, but you may not choose two houses at adjacent positions.",
        "Return the greatest total amount that can be collected. Return `0` for an empty list.",
    ),
    "decode-ways": _paragraphs(
        "The numbers `1` through `26` represent the letters `A` through `Z`.",
        "Split the digit string `s` into valid one-digit or two-digit numbers. A `0` cannot be decoded by itself, and numbers with a leading zero are invalid.",
        "Return the number of complete decodings of the string.",
    ),
    "longest-increasing-subsequence": _paragraphs(
        "A subsequence keeps the original order of selected values but may skip values between them.",
        "Find a subsequence of `nums` in which every selected value is strictly greater than the one before it.",
        "Return the greatest possible length of such a subsequence.",
    ),
    "word-break": _paragraphs(
        "You are given a string `s` and a list of nonempty dictionary words.",
        "Determine whether every character of `s` can be covered, in order, by a sequence of dictionary words. A dictionary word may be used more than once.",
        "Return `True` when a complete segmentation exists. Otherwise, return `False`.",
    ),
    "combination-sum": _paragraphs(
        "`candidates` contains distinct positive integers. Any candidate may be selected more than once.",
        "Find every unique combination whose values add up exactly to `target`. Values within each combination must be in nondecreasing order.",
        "Return the combinations in lexicographic order.",
    ),
    "permutations": _paragraphs(
        "`nums` contains distinct integers.",
        "A permutation contains every input value exactly once in a particular order. Generate every possible permutation.",
        "Return the permutations in lexicographic order.",
    ),
    "generate-parentheses": _paragraphs(
        "Given `n`, form strings containing exactly `n` opening parentheses and `n` closing parentheses.",
        "A string is valid when every prefix has at least as many opening parentheses as closing parentheses, and all parentheses are matched by the end.",
        "Return every distinct valid string in lexicographic order.",
    ),
    "subsets": _paragraphs(
        "`nums` contains distinct integers.",
        "Return every subset of its values, including the empty subset and the full set. A value may appear at most once in a subset.",
        "Sort values within each subset. Order the result by subset length, then lexicographically among subsets of the same length.",
    ),
}


def _problem(
    *,
    id: str,
    title: str,
    difficulty: str,
    tags: list[str],
    summary: str,
    description: str,
    signature: str,
    examples: list[tuple[str, str, str]],
    constraints: list[str],
    guide: list[str],
    hints: list[str],
    tests: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "difficulty": difficulty,
        "tags": tags,
        "summary": summary,
        "description": LEARNER_DESCRIPTIONS.get(id, description),
        "signature": signature,
        "starter_code": f"{signature}\n    # Write your solution here\n    pass\n",
        "examples": [
            {"input": example_input, "output": output, "explanation": explanation}
            for example_input, output, explanation in examples
        ],
        "constraints": constraints,
        "guide": guide,
        "hints": hints,
        "tests": tests,
    }


PROBLEMS = [
    _problem(
        id="two-sum",
        title="Two Sum",
        difficulty="Easy",
        tags=["Arrays", "Hash Map"],
        summary="Return the indices of two distinct values whose sum equals a target.",
        description=(
            "You are given an integer list `nums` and an integer `target`. Find two different positions "
            "whose values add up exactly to `target`, and return their indices in increasing order. "
            "Exactly one valid pair exists, so you do not need to handle multiple answers. You may not "
            "use the same element twice, even when the required values are equal."
        ),
        signature="def solve(nums, target):",
        examples=[
            (
                "nums = [2, 7, 11, 15], target = 9",
                "[0, 1]",
                "At index `0`, the value `2` needs a complement of `7`. That value appears at "
                "index `1`, and `2 + 7 = 9`, so the required indices are `[0, 1]`.",
            ),
            (
                "nums = [3, 2, 4], target = 6",
                "[1, 2]",
                "The first value, `3`, would need a second `3`, which this input does not contain. "
                "At index `1`, the value `2` needs `4`; it appears at index `2`, so the answer is `[1, 2]`.",
            ),
            (
                "nums = [3, 3], target = 6",
                "[0, 1]",
                "The complement of the first `3` is another `3`. The match at index `1` is a different "
                "element, so `[0, 1]` satisfies both the target and the no-reuse rule.",
            ),
        ],
        constraints=["2 <= len(nums) <= 10,000", "Exactly one valid pair exists.", "Return the smaller index first."],
        guide=[
            "For a current value `x`, what second value would complete the target?",
            "What information from earlier positions should be stored for constant-time lookup?",
            "Should you check for the complement before or after storing the current value? Why?",
            "State the invariant and the expected time and space complexity.",
        ],
        hints=[
            "The needed complement is `target - nums[i]`.",
            "Map each previously seen value to its index.",
            "Check the complement before inserting the current value so one element is not reused.",
            "A single left-to-right pass is enough.",
        ],
        tests=[
            {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"args": [[3, 2, 4], 6], "expected": [1, 2]},
            {"args": [[3, 3], 6], "expected": [0, 1]},
            {"args": [[-3, 4, 3, 90], 0], "expected": [0, 2]},
        ],
    ),
    _problem(
        id="valid-parentheses",
        title="Valid Parentheses",
        difficulty="Easy",
        tags=["Strings", "Stack"],
        summary="Check whether brackets are balanced, matched, and correctly nested.",
        description=(
            "You are given a string containing only `(`, `)`, `[`, `]`, `{`, and `}`. Return `True` only "
            "when every opening bracket is closed by the same bracket type and closures occur in the "
            "correct nesting order. A closing bracket cannot appear before its matching opener, and no "
            "unmatched opening brackets may remain after the scan."
        ),
        signature="def solve(s):",
        examples=[
            ("s = '()[]{}'", "True", "Each pair closes correctly and the pairs do not interfere."),
            ("s = '([{}])'", "True", "The brackets are nested in last-opened, first-closed order."),
            ("s = '(]'", "False", "A parenthesis cannot be closed by a square bracket."),
        ],
        constraints=["0 <= len(s) <= 20,000", "The string contains bracket characters only."],
        guide=[
            "Which data structure remembers the most recent unmatched opening bracket?",
            "What must be checked whenever a closing bracket appears?",
            "What should happen when a closer appears while no opener is available?",
            "What final condition proves that all opening brackets were matched?",
        ],
        hints=[
            "Push opening brackets onto a stack.",
            "Map each closing bracket to the opening bracket it requires.",
            "A closing bracket must match the current top of the stack.",
            "The stack must be empty after processing the entire string.",
        ],
        tests=[
            {"args": ["()[]{}"], "expected": True},
            {"args": ["(]"], "expected": False},
            {"args": ["([{}])"], "expected": True},
            {"args": ["(("], "expected": False},
            {"args": [""], "expected": True},
        ],
    ),
    _problem(
        id="best-stock-profit",
        title="Best Time to Buy and Sell Stock",
        difficulty="Easy",
        tags=["Arrays", "Greedy"],
        summary="Find the largest profit from one buy followed by one later sell.",
        description=(
            "Each value in `prices` is the stock price on one day. Choose one day to buy and a strictly "
            "later day to sell, then return the maximum possible profit. You may complete at most one "
            "transaction. When every later price is lower than or equal to its earlier prices, return `0`."
        ),
        signature="def solve(prices):",
        examples=[
            ("prices = [7, 1, 5, 3, 6, 4]", "5", "Buy at `1` and sell later at `6`."),
            ("prices = [7, 6, 4, 3, 1]", "0", "No legal buy-then-sell pair produces a positive profit."),
            ("prices = [2, 4, 1]", "2", "Buy at `2` and sell at `4`; the later `1` does not help."),
        ],
        constraints=["1 <= len(prices) <= 100,000", "Prices are non-negative integers.", "The buy day must precede the sell day."],
        guide=[
            "When considering a sale today, which earlier price matters most?",
            "How can that earlier value be updated while scanning once?",
            "When should the current candidate profit be compared with the best profit?",
            "Describe the invariant maintained after processing each day.",
        ],
        hints=[
            "Track the minimum price seen so far.",
            "The profit from selling today is `price - minimum_so_far`.",
            "Update both the best profit and the minimum during one pass.",
            "Initialize the best profit to zero so declining inputs are handled naturally.",
        ],
        tests=[
            {"args": [[7, 1, 5, 3, 6, 4]], "expected": 5},
            {"args": [[7, 6, 4, 3, 1]], "expected": 0},
            {"args": [[1, 2]], "expected": 1},
            {"args": [[2]], "expected": 0},
            {"args": [[2, 4, 1]], "expected": 2},
        ],
    ),
    _problem(
        id="binary-search",
        title="Binary Search",
        difficulty="Easy",
        tags=["Arrays", "Binary Search"],
        summary="Locate a target in a sorted list using logarithmic search.",
        description=(
            "You are given an ascending list of distinct integers and a target value. Return the target's "
            "index when it is present; otherwise return `-1`. Your algorithm should repeatedly discard half "
            "of the remaining search interval and run in `O(log n)` time."
        ),
        signature="def solve(nums, target):",
        examples=[
            ("nums = [-1, 0, 3, 5, 9, 12], target = 9", "4", "The target appears at zero-based index `4`."),
            ("nums = [-1, 0, 3, 5, 9, 12], target = 2", "-1", "The target is not in the sorted list."),
            ("nums = [5], target = 5", "0", "A one-element search interval is still valid."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "Values are distinct and sorted in ascending order.", "Target `O(log n)` time."],
        guide=[
            "What do the left and right boundaries represent at every iteration?",
            "How is the midpoint used to eliminate half of the search space?",
            "Which boundary changes when the midpoint value is too small or too large?",
            "Which loop condition still checks a one-element interval?",
        ],
        hints=[
            "Use inclusive `left` and `right` boundaries.",
            "Loop while `left <= right`.",
            "If `nums[mid] < target`, move `left` to `mid + 1`.",
            "Return `-1` only after the interval becomes empty.",
        ],
        tests=[
            {"args": [[-1, 0, 3, 5, 9, 12], 9], "expected": 4},
            {"args": [[-1, 0, 3, 5, 9, 12], 2], "expected": -1},
            {"args": [[5], 5], "expected": 0},
            {"args": [[2, 4, 6, 8], 2], "expected": 0},
            {"args": [[2, 4, 6, 8], 8], "expected": 3},
            {"args": [[], 4], "expected": -1},
        ],
    ),
    _problem(
        id="contains-duplicate",
        title="Contains Duplicate",
        difficulty="Easy",
        tags=["Arrays", "Hash Set"],
        summary="Determine whether any value appears more than once.",
        description=(
            "Given an integer list `nums`, return `True` when at least one value occurs in two or more "
            "positions. Return `False` when every element is unique. The input order does not affect the "
            "answer, but your solution should avoid comparing every pair."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [1, 2, 3, 1]", "True", "The value `1` appears at indices `0` and `3`."),
            ("nums = [1, 2, 3, 4]", "False", "All four values are distinct."),
            ("nums = []", "False", "An empty list contains no duplicate pair."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "Values may be negative."],
        guide=[
            "What compact structure can represent the values already encountered?",
            "At what point can the function return immediately?",
            "How does converting the list to a set relate to duplicate detection?",
            "Compare the time and space costs of sorting versus hashing.",
        ],
        hints=[
            "A set stores unique values.",
            "Return `True` as soon as the current value is already in the set.",
            "Alternatively, compare `len(nums)` with `len(set(nums))`.",
            "A hash-set solution is expected to run in linear average time.",
        ],
        tests=[
            {"args": [[1, 2, 3, 1]], "expected": True},
            {"args": [[1, 2, 3, 4]], "expected": False},
            {"args": [[]], "expected": False},
            {"args": [[-1, -1]], "expected": True},
        ],
    ),
    _problem(
        id="valid-anagram",
        title="Valid Anagram",
        difficulty="Easy",
        tags=["Strings", "Hash Map"],
        summary="Check whether two strings contain the same characters with the same frequencies.",
        description=(
            "Two strings are anagrams when one can be rearranged to form the other without adding or "
            "removing characters. Given lowercase strings `s` and `t`, return `True` if their character "
            "frequency counts are identical. Character positions do not matter, but repeated characters do."
        ),
        signature="def solve(s, t):",
        examples=[
            ("s = 'anagram', t = 'nagaram'", "True", "Both strings contain the same letters with the same counts."),
            ("s = 'rat', t = 'car'", "False", "The first string contains `t`, while the second contains `c`."),
            ("s = 'aacc', t = 'ccac'", "False", "The count of `a` differs between the strings."),
        ],
        constraints=["0 <= len(s), len(t) <= 100,000", "Inputs contain lowercase English letters."],
        guide=[
            "What immediate length check can reject impossible pairs?",
            "Which quantity must be equal for every character?",
            "Can one frequency map be incremented and decremented?",
            "What condition on the final counts proves the strings are anagrams?",
        ],
        hints=[
            "Different lengths can never be anagrams.",
            "Count characters in both strings or use one net-count dictionary.",
            "Increment for `s` and decrement for `t`.",
            "Every final count must equal zero.",
        ],
        tests=[
            {"args": ["anagram", "nagaram"], "expected": True},
            {"args": ["rat", "car"], "expected": False},
            {"args": ["aacc", "ccac"], "expected": False},
            {"args": ["", ""], "expected": True},
        ],
    ),
    _problem(
        id="merge-sorted-arrays",
        title="Merge Two Sorted Arrays",
        difficulty="Easy",
        tags=["Arrays", "Two Pointers"],
        summary="Combine two sorted lists into one sorted result.",
        description=(
            "You are given two integer lists, each already sorted in nondecreasing order. Return a new list "
            "containing every value from both inputs, also in nondecreasing order. Duplicate values must be "
            "preserved. Build the result by exploiting the existing order rather than sorting all values again."
        ),
        signature="def solve(a, b):",
        examples=[
            ("a = [1, 3, 5], b = [2, 4, 6]", "[1, 2, 3, 4, 5, 6]", "Repeatedly choose the smaller current value."),
            ("a = [1, 2, 2], b = [2, 3]", "[1, 2, 2, 2, 3]", "All duplicate `2` values remain in the result."),
            ("a = [], b = [4, 7]", "[4, 7]", "When one input is empty, append the other input."),
        ],
        constraints=["0 <= len(a), len(b) <= 100,000", "Both inputs are sorted in nondecreasing order.", "Return a new list."],
        guide=[
            "What does each pointer identify in its respective list?",
            "How do you choose the next smallest output value?",
            "What happens after one pointer reaches the end?",
            "Why is the total running time linear in the combined input size?",
        ],
        hints=[
            "Maintain one pointer for each list.",
            "Append the smaller pointed-to value and advance only that pointer.",
            "After the main loop, append the unprocessed suffix from either list.",
            "Each input element is visited exactly once.",
        ],
        tests=[
            {"args": [[1, 3, 5], [2, 4, 6]], "expected": [1, 2, 3, 4, 5, 6]},
            {"args": [[1, 2, 2], [2, 3]], "expected": [1, 2, 2, 2, 3]},
            {"args": [[], [4, 7]], "expected": [4, 7]},
            {"args": [[-3, 0], []], "expected": [-3, 0]},
        ],
    ),
    _problem(
        id="move-zeroes",
        title="Move Zeroes",
        difficulty="Easy",
        tags=["Arrays", "Two Pointers"],
        summary="Move all zero values to the end while preserving nonzero order.",
        description=(
            "Given an integer list, return a list in which every nonzero value appears first in its original "
            "relative order, followed by all zero values. The output must have the same length and contain the "
            "same multiset of values as the input. Do not sort, because sorting would change nonzero order."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [0, 1, 0, 3, 12]", "[1, 3, 12, 0, 0]", "The nonzero sequence `1, 3, 12` stays in the same order."),
            ("nums = [0, 0, 1]", "[1, 0, 0]", "The single nonzero value moves before both zeroes."),
            ("nums = [1, 2]", "[1, 2]", "A list without zeroes is unchanged."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "Return the transformed list.", "Preserve the relative order of nonzero values."],
        guide=[
            "What position should receive the next nonzero value?",
            "How can one scan collect nonzero values without reordering them?",
            "How many zeroes must be added after all nonzero values are placed?",
            "Can the same idea be implemented in place with two pointers?",
        ],
        hints=[
            "Track a write position for the next nonzero value.",
            "Scan left to right and copy each nonzero value forward.",
            "Fill the remaining suffix with zeroes.",
            "A compact alternative is `[x for x in nums if x != 0]` plus the required number of zeroes.",
        ],
        tests=[
            {"args": [[0, 1, 0, 3, 12]], "expected": [1, 3, 12, 0, 0]},
            {"args": [[0, 0, 1]], "expected": [1, 0, 0]},
            {"args": [[1, 2]], "expected": [1, 2]},
            {"args": [[]], "expected": []},
        ],
    ),
    _problem(
        id="maximum-subarray",
        title="Maximum Subarray",
        difficulty="Easy",
        tags=["Arrays", "Dynamic Programming"],
        summary="Find the largest sum among all contiguous, nonempty subarrays.",
        description=(
            "Given a nonempty integer list, choose a contiguous block containing at least one element and "
            "return the largest possible sum. The selected block may start and end anywhere, but elements "
            "cannot be skipped inside it. Inputs may contain only negative values, so an empty subarray is not allowed."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "6", "The subarray `[4, -1, 2, 1]` has sum `6`."),
            ("nums = [1]", "1", "The only valid nonempty subarray contains the single element."),
            ("nums = [-3, -2, -5]", "-2", "The best choice is the least-negative single value."),
        ],
        constraints=["1 <= len(nums) <= 100,000", "The chosen subarray must be contiguous and nonempty."],
        guide=[
            "At each index, should the best subarray ending here extend the previous one or restart?",
            "What state summarizes the best sum ending at the current position?",
            "Why is a separate global maximum still needed?",
            "How should initialization handle an all-negative input?",
        ],
        hints=[
            "Let `current` be the best sum of a subarray ending at the current value.",
            "Update with `current = max(value, current + value)`.",
            "Track the largest `current` observed.",
            "Initialize from the first element, not from zero.",
        ],
        tests=[
            {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
            {"args": [[1]], "expected": 1},
            {"args": [[5, 4, -1, 7, 8]], "expected": 23},
            {"args": [[-3, -2, -5]], "expected": -2},
        ],
    ),
    _problem(
        id="majority-element",
        title="Majority Element",
        difficulty="Easy",
        tags=["Arrays", "Greedy"],
        summary="Find the value appearing more than half of the time.",
        description=(
            "A majority element appears strictly more than `len(nums) // 2` times. Given a nonempty list "
            "where such an element is guaranteed to exist, return that value. Your solution should ideally "
            "use constant extra space rather than storing a full frequency table."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [3, 2, 3]", "3", "The value `3` appears twice in a list of length three."),
            ("nums = [2, 2, 1, 1, 1, 2, 2]", "2", "The value `2` appears four times, which is more than half."),
            ("nums = [9]", "9", "The only element is automatically the majority."),
        ],
        constraints=["1 <= len(nums) <= 100,000", "A majority element is guaranteed to exist."],
        guide=[
            "How can equal values reinforce a candidate while different values cancel it?",
            "When should a new candidate be selected?",
            "Why can all non-majority values collectively cancel only part of the majority?",
            "What are the time and extra-space costs of the voting approach?",
        ],
        hints=[
            "Maintain a candidate and a counter.",
            "When the counter reaches zero, choose the current value as the new candidate.",
            "Increment for the candidate and decrement for a different value.",
            "The guaranteed majority is the final candidate.",
        ],
        tests=[
            {"args": [[3, 2, 3]], "expected": 3},
            {"args": [[2, 2, 1, 1, 1, 2, 2]], "expected": 2},
            {"args": [[9]], "expected": 9},
            {"args": [[1, 1, 1, 2, 3]], "expected": 1},
        ],
    ),
    _problem(
        id="first-unique-character",
        title="First Unique Character",
        difficulty="Easy",
        tags=["Strings", "Hash Map"],
        summary="Return the index of the first character that occurs exactly once.",
        description=(
            "Given a lowercase string `s`, find the earliest position whose character appears exactly once "
            "in the entire string. Return that zero-based index, or `-1` when every character is repeated. "
            "The word 'first' refers to the original string order, not alphabetical order."
        ),
        signature="def solve(s):",
        examples=[
            ("s = 'leetcode'", "0", "`l` occurs once and appears before every other unique character."),
            ("s = 'loveleetcode'", "2", "The character `v` at index `2` is the first unique character."),
            ("s = 'aabb'", "-1", "Every character appears twice."),
        ],
        constraints=["0 <= len(s) <= 100,000", "The string contains lowercase English letters."],
        guide=[
            "What information must be known before deciding whether a character is unique?",
            "Why is a second pass useful after counting frequencies?",
            "What order should the second pass follow?",
            "When can the function return immediately?",
        ],
        hints=[
            "Count the frequency of every character first.",
            "Scan the original string from left to right afterward.",
            "The first character with frequency `1` gives the answer.",
            "Return `-1` if no such character exists.",
        ],
        tests=[
            {"args": ["leetcode"], "expected": 0},
            {"args": ["loveleetcode"], "expected": 2},
            {"args": ["aabb"], "expected": -1},
            {"args": [""], "expected": -1},
        ],
    ),
    _problem(
        id="ransom-note",
        title="Ransom Note",
        difficulty="Easy",
        tags=["Strings", "Hash Map"],
        summary="Check whether one string can be assembled from another string's characters.",
        description=(
            "You are given `note` and `magazine`. Return `True` if every character required by `note` can be "
            "taken from `magazine`, with each magazine character used at most once. Character order is irrelevant, "
            "but frequency matters: needing two copies requires at least two available copies."
        ),
        signature="def solve(note, magazine):",
        examples=[
            ("note = 'a', magazine = 'b'", "False", "The required character `a` is unavailable."),
            ("note = 'aa', magazine = 'aab'", "True", "The magazine supplies two `a` characters."),
            ("note = '', magazine = 'anything'", "True", "An empty note requires no characters."),
        ],
        constraints=["0 <= len(note), len(magazine) <= 100,000", "Inputs contain lowercase English letters."],
        guide=[
            "Which string provides the available character inventory?",
            "How should the inventory change as note characters are consumed?",
            "What condition identifies an unavailable character?",
            "Which input should be counted to minimize unnecessary work?",
        ],
        hints=[
            "Build character counts from `magazine`.",
            "For each note character, verify its remaining count is positive.",
            "Decrement the count after consuming a character.",
            "Return early as soon as a requirement cannot be met.",
        ],
        tests=[
            {"args": ["a", "b"], "expected": False},
            {"args": ["aa", "aab"], "expected": True},
            {"args": ["aa", "ab"], "expected": False},
            {"args": ["", "anything"], "expected": True},
        ],
    ),
    _problem(
        id="valid-palindrome",
        title="Valid Palindrome",
        difficulty="Easy",
        tags=["Strings", "Two Pointers"],
        summary="Check whether a string reads the same after normalization.",
        description=(
            "Return `True` if `s` is a palindrome after ignoring every non-alphanumeric character and treating "
            "uppercase and lowercase letters as equal. A palindrome reads the same from left to right and right "
            "to left. The empty normalized string is considered a palindrome."
        ),
        signature="def solve(s):",
        examples=[
            ("s = 'A man, a plan, a canal: Panama'", "True", "Normalization gives `amanaplanacanalpanama`."),
            ("s = 'race a car'", "False", "Normalization gives `raceacar`, which is not symmetric."),
            ("s = ' ' ", "True", "No alphanumeric characters remain after normalization."),
        ],
        constraints=["0 <= len(s) <= 200,000", "Letters and digits are alphanumeric."],
        guide=[
            "How can two pointers skip characters that do not participate in the comparison?",
            "When both pointers reference alphanumeric characters, what must be compared?",
            "When can a mismatch be returned immediately?",
            "What does it mean when the pointers cross without a mismatch?",
        ],
        hints=[
            "Start one pointer at each end of the string.",
            "Advance past non-alphanumeric characters before comparing.",
            "Compare lowercase versions of the remaining characters.",
            "Move both pointers inward after a successful comparison.",
        ],
        tests=[
            {"args": ["A man, a plan, a canal: Panama"], "expected": True},
            {"args": ["race a car"], "expected": False},
            {"args": [" "], "expected": True},
            {"args": ["0P"], "expected": False},
        ],
    ),
    _problem(
        id="reverse-words",
        title="Reverse Words in a String",
        difficulty="Easy",
        tags=["Strings"],
        summary="Reverse word order and normalize extra spaces.",
        description=(
            "A word is a maximal sequence of non-space characters. Given a string that may contain leading, "
            "trailing, or repeated spaces, return the words in reverse order separated by exactly one space. "
            "Do not reverse the characters inside individual words."
        ),
        signature="def solve(s):",
        examples=[
            ("s = 'the sky is blue'", "'blue is sky the'", "The four words are reordered from last to first."),
            ("s = '  hello world  '", "'world hello'", "Leading and trailing spaces are removed."),
            ("s = 'a good   example'", "'example good a'", "Multiple spaces collapse to one separator."),
        ],
        constraints=["0 <= len(s) <= 200,000", "Words contain non-space characters."],
        guide=[
            "How can the input be separated into words while automatically ignoring repeated spaces?",
            "Which sequence operation reverses the word order?",
            "How should the final words be joined to guarantee one space between them?",
            "What should an all-space input return?",
        ],
        hints=[
            "Python's `split()` without an argument removes extra whitespace.",
            "Reverse the resulting list of words.",
            "Join with a single space.",
            "An empty word list joins to the empty string.",
        ],
        tests=[
            {"args": ["the sky is blue"], "expected": "blue is sky the"},
            {"args": ["  hello world  "], "expected": "world hello"},
            {"args": ["a good   example"], "expected": "example good a"},
            {"args": ["   "], "expected": ""},
        ],
    ),
    _problem(
        id="missing-number",
        title="Missing Number",
        difficulty="Easy",
        tags=["Arrays", "Math"],
        summary="Find the missing value from the range zero through n.",
        description=(
            "The list `nums` contains `n` distinct numbers selected from the complete range `0` through `n`. "
            "Exactly one value from that range is absent. Return the missing value without relying on the input "
            "being sorted."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [3, 0, 1]", "2", "The complete range is `0, 1, 2, 3`; only `2` is missing."),
            ("nums = [0, 1]", "2", "The missing value may be the upper endpoint `n`."),
            ("nums = [1]", "0", "The missing value may also be zero."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "All values are distinct.", "Every value lies between `0` and `len(nums)` inclusive."],
        guide=[
            "What is the expected sum of all integers from zero through n?",
            "How does subtracting the actual sum reveal the missing value?",
            "Can XOR provide an alternative that avoids large arithmetic sums?",
            "What edge cases occur at the two endpoints of the range?",
        ],
        hints=[
            "Let `n = len(nums)`.",
            "The expected sum is `n * (n + 1) // 2`.",
            "Subtract `sum(nums)` from the expected sum.",
            "The same formula handles missing `0` and missing `n`.",
        ],
        tests=[
            {"args": [[3, 0, 1]], "expected": 2},
            {"args": [[0, 1]], "expected": 2},
            {"args": [[1]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
    ),
    _problem(
        id="intersection-unique",
        title="Intersection of Two Arrays",
        difficulty="Easy",
        tags=["Arrays", "Hash Set"],
        summary="Return the distinct values shared by two arrays.",
        description=(
            "Given integer lists `a` and `b`, return every distinct value that appears in both lists. Each shared "
            "value must appear exactly once in the output, regardless of its frequency in either input. Return "
            "the result sorted in ascending order so the output is deterministic."
        ),
        signature="def solve(a, b):",
        examples=[
            ("a = [1, 2, 2, 1], b = [2, 2]", "[2]", "`2` is shared, but appears only once in the output."),
            ("a = [4, 9, 5], b = [9, 4, 9, 8, 4]", "[4, 9]", "Both `4` and `9` occur in each list."),
            ("a = [1, 3], b = [2, 4]", "[]", "The inputs have no common values."),
        ],
        constraints=["0 <= len(a), len(b) <= 100,000", "Return unique shared values in ascending order."],
        guide=[
            "Which operation on sets directly represents shared values?",
            "Why do sets automatically remove repeated occurrences?",
            "What final step is required by the output ordering contract?",
            "Which input could be converted to a set when optimizing memory manually?",
        ],
        hints=[
            "Convert both lists to sets.",
            "Use set intersection.",
            "Convert the intersection back to a list.",
            "Sort the final list before returning it.",
        ],
        tests=[
            {"args": [[1, 2, 2, 1], [2, 2]], "expected": [2]},
            {"args": [[4, 9, 5], [9, 4, 9, 8, 4]], "expected": [4, 9]},
            {"args": [[1, 3], [2, 4]], "expected": []},
            {"args": [[], [1]], "expected": []},
        ],
    ),
    _problem(
        id="single-number",
        title="Single Number",
        difficulty="Easy",
        tags=["Arrays", "Bit Manipulation"],
        summary="Find the one value that does not have a matching duplicate.",
        description=(
            "Every value in `nums` appears exactly twice except for one value, which appears once. Return that "
            "single value. The input may include negative integers. Aim for linear time and constant extra space."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [2, 2, 1]", "1", "The two `2` values pair off, leaving `1`."),
            ("nums = [4, 1, 2, 1, 2]", "4", "Both `1` and `2` occur twice; `4` occurs once."),
            ("nums = [-7]", "-7", "A one-element input contains the single value directly."),
        ],
        constraints=["1 <= len(nums) <= 100,000", "Exactly one value appears once; all others appear twice."],
        guide=[
            "Which bitwise operation cancels equal values?",
            "What are the identity and self-cancellation properties of XOR?",
            "Why does input order not matter for repeated XOR operations?",
            "What accumulator value should be used initially?",
        ],
        hints=[
            "For any integer `x`, `x ^ x` equals zero.",
            "For any integer `x`, `x ^ 0` equals `x`.",
            "XOR every value into one accumulator.",
            "All pairs cancel, leaving the single value.",
        ],
        tests=[
            {"args": [[2, 2, 1]], "expected": 1},
            {"args": [[4, 1, 2, 1, 2]], "expected": 4},
            {"args": [[-7]], "expected": -7},
            {"args": [[-1, 3, 3]], "expected": -1},
        ],
    ),
    _problem(
        id="climbing-stairs",
        title="Climbing Stairs",
        difficulty="Easy",
        tags=["Dynamic Programming"],
        summary="Count the ways to reach the top using one-step and two-step moves.",
        description=(
            "A staircase has `n` steps. Starting below step one, you may climb either one or two steps at a time. "
            "Return the number of distinct move sequences that land exactly on step `n`. Sequences with the same "
            "moves in a different order count separately."
        ),
        signature="def solve(n):",
        examples=[
            ("n = 2", "2", "The valid sequences are `1+1` and `2`."),
            ("n = 3", "3", "The valid sequences are `1+1+1`, `1+2`, and `2+1`."),
            ("n = 5", "8", "The count follows the Fibonacci-style recurrence."),
        ],
        constraints=["1 <= n <= 45", "Each move has size one or two."],
        guide=[
            "What must the final move into step n be?",
            "How does that split the answer into smaller staircase counts?",
            "Which two previous values are sufficient to compute the next count?",
            "What base cases make the recurrence valid?",
        ],
        hints=[
            "Ways to reach step `n` equal ways to reach `n-1` plus ways to reach `n-2`.",
            "Use base values for one and two steps.",
            "Only keep the previous two counts.",
            "Iterate upward instead of using exponential recursion.",
        ],
        tests=[
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 2},
            {"args": [3], "expected": 3},
            {"args": [5], "expected": 8},
            {"args": [10], "expected": 89},
        ],
    ),
    _problem(
        id="flood-fill",
        title="Flood Fill",
        difficulty="Easy",
        tags=["Matrix", "Graph Traversal", "BFS/DFS"],
        summary="Recolor a connected region in a grid.",
        description=(
            "The matrix `image` stores a color integer in each cell. Starting from `(sr, sc)`, recolor that cell "
            "and every cell connected to it through up, down, left, or right moves that has the same original color. "
            "Return the resulting matrix. Diagonal contact does not connect regions."
        ),
        signature="def solve(image, sr, sc, color):",
        examples=[
            ("image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1, color = 2", "[[2,2,2],[2,2,0],[2,0,1]]", "Only the four-directionally connected region of `1` values is recolored."),
            ("image = [[0,0,0],[0,0,0]], sr = 0, sc = 0, color = 0", "[[0,0,0],[0,0,0]]", "The requested color already matches the original color."),
            ("image = [[1]], sr = 0, sc = 0, color = 3", "[[3]]", "The single cell forms the whole connected region."),
        ],
        constraints=["1 <= rows, cols <= 200", "Coordinates are valid.", "Connectivity is four-directional.", "Return the modified matrix."],
        guide=[
            "What original color defines membership in the region?",
            "Which neighboring coordinates should be explored from each cell?",
            "How can recoloring also mark a cell as visited?",
            "What special case prevents unnecessary traversal when the color is unchanged?",
        ],
        hints=[
            "Save the starting cell's original color.",
            "If the new color equals the original color, return immediately.",
            "Use DFS or BFS over four-directional neighbors with the original color.",
            "Recolor a cell when it is first visited so it is not processed again.",
        ],
        tests=[
            {"args": [[[1,1,1],[1,1,0],[1,0,1]], 1, 1, 2], "expected": [[2,2,2],[2,2,0],[2,0,1]]},
            {"args": [[[0,0,0],[0,0,0]], 0, 0, 0], "expected": [[0,0,0],[0,0,0]]},
            {"args": [[[1]], 0, 0, 3], "expected": [[3]]},
            {"args": [[[1,2],[2,2]], 0, 0, 9], "expected": [[9,2],[2,2]]},
        ],
    ),
    _problem(
        id="counting-bits",
        title="Counting Bits",
        difficulty="Easy",
        tags=["Dynamic Programming", "Bit Manipulation"],
        summary="Count set bits for every integer from zero through n.",
        description=(
            "Given a nonnegative integer `n`, return a list `answer` of length `n + 1` where `answer[i]` is the "
            "number of `1` bits in the binary representation of `i`. Compute the full range efficiently rather "
            "than converting every number to a binary string independently."
        ),
        signature="def solve(n):",
        examples=[
            ("n = 2", "[0, 1, 1]", "Binary forms are `0`, `1`, and `10`."),
            ("n = 5", "[0, 1, 1, 2, 1, 2]", "`3` and `5` each contain two set bits."),
            ("n = 0", "[0]", "The binary representation of zero has no set bits."),
        ],
        constraints=["0 <= n <= 100,000", "Return counts for every integer in the inclusive range `0..n`."],
        guide=[
            "How is the bit count of `i` related to the bit count of `i // 2`?",
            "What information does `i % 2` or `i & 1` provide?",
            "Why are the required smaller answers already available during a forward loop?",
            "What should the first output value be?",
        ],
        hints=[
            "Removing the lowest bit from `i` gives `i >> 1`.",
            "The removed bit is `i & 1`.",
            "Use `answer[i] = answer[i >> 1] + (i & 1)`.",
            "Initialize `answer` with the count for zero.",
        ],
        tests=[
            {"args": [0], "expected": [0]},
            {"args": [2], "expected": [0, 1, 1]},
            {"args": [5], "expected": [0, 1, 1, 2, 1, 2]},
            {"args": [8], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1]},
        ],
    ),
    _problem(
        id="longest-unique-substring",
        title="Longest Substring Without Repeating Characters",
        difficulty="Medium",
        tags=["Strings", "Sliding Window", "Hash Map"],
        summary="Find the longest contiguous substring whose characters are all distinct.",
        description=(
            "Given a string `s`, return the length of its longest contiguous substring containing no repeated "
            "character. A substring must occupy consecutive positions, so characters cannot be skipped. When a "
            "duplicate enters the current window, move the left boundary only far enough to restore uniqueness."
        ),
        signature="def solve(s):",
        examples=[
            ("s = 'abcabcbb'", "3", "The longest unique substrings include `abc`, with length `3`."),
            ("s = 'bbbbb'", "1", "Any valid substring can contain only one `b`."),
            ("s = 'pwwkew'", "3", "`wke` has length `3`; `pwke` is not contiguous."),
        ],
        constraints=["0 <= len(s) <= 100,000", "The answer is a length, not the substring itself."],
        guide=[
            "What invariant should the current window satisfy?",
            "What information about each character allows the left boundary to jump efficiently?",
            "Why must the left boundary never move backward?",
            "When should the maximum window length be updated?",
        ],
        hints=[
            "Use a sliding window with `left` and `right` boundaries.",
            "Store the most recent index of each character.",
            "On a duplicate inside the window, set `left` to one after its previous index.",
            "Update the answer with `right - left + 1` after restoring the invariant.",
        ],
        tests=[
            {"args": ["abcabcbb"], "expected": 3},
            {"args": ["bbbbb"], "expected": 1},
            {"args": ["pwwkew"], "expected": 3},
            {"args": [""], "expected": 0},
            {"args": ["abba"], "expected": 2},
        ],
    ),
    _problem(
        id="product-except-self",
        title="Product of Array Except Self",
        difficulty="Medium",
        tags=["Arrays", "Prefix/Suffix"],
        summary="Compute every index's product without using division.",
        description=(
            "For each index `i`, return the product of all values in `nums` except `nums[i]`. Division is not "
            "allowed, and the solution should run in linear time. Zero values must be handled naturally rather "
            "than through special-case division logic."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [1, 2, 3, 4]", "[24, 12, 8, 6]", "At index `1`, the product is `1 * 3 * 4 = 12`."),
            ("nums = [-1, 1, 0, -3, 3]", "[0, 0, 9, 0, 0]", "Only the zero position receives the product of all nonzero values."),
            ("nums = [2, 3]", "[3, 2]", "Each output contains the other input value."),
        ],
        constraints=["2 <= len(nums) <= 100,000", "Do not use division.", "Target `O(n)` time."],
        guide=[
            "What product should be stored for the values strictly to the left of each index?",
            "How can a reverse pass supply the product strictly to the right?",
            "Can the output array itself store the prefix products?",
            "What running value is needed during the reverse pass?",
        ],
        hints=[
            "First fill output positions with the product of values to their left.",
            "Maintain a running suffix product while scanning right to left.",
            "Multiply each stored prefix by the current suffix.",
            "Update the suffix only after using it for the current index.",
        ],
        tests=[
            {"args": [[1, 2, 3, 4]], "expected": [24, 12, 8, 6]},
            {"args": [[-1, 1, 0, -3, 3]], "expected": [0, 0, 9, 0, 0]},
            {"args": [[2, 3]], "expected": [3, 2]},
            {"args": [[0, 0]], "expected": [0, 0]},
        ],
    ),
    _problem(
        id="group-anagrams",
        title="Group Anagrams",
        difficulty="Medium",
        tags=["Strings", "Hash Map"],
        summary="Group words that have identical character-frequency signatures.",
        description=(
            "Given lowercase words, place words into the same group when their letters can be rearranged to match. "
            "Preserve the original order of words inside each group, and order the groups by the first input position "
            "belonging to that group. This ordering rule makes the expected output deterministic."
        ),
        signature="def solve(words):",
        examples=[
            ("words = ['eat','tea','tan','ate','nat','bat']", "[['eat','tea','ate'],['tan','nat'],['bat']]", "The first signature appears at `eat`, the second at `tan`, and the third at `bat`."),
            ("words = ['']", "[['']]", "The empty string is an anagram of itself."),
            ("words = ['a','a']", "[['a','a']]", "Equal words share one group and retain their input order."),
        ],
        constraints=["0 <= len(words) <= 20,000", "Words contain lowercase English letters.", "Preserve the specified group and member ordering."],
        guide=[
            "What canonical key is identical for all anagrams?",
            "Would a sorted-character key or a 26-count tuple fit the constraints?",
            "How does normal dictionary insertion order preserve first group appearance?",
            "What should be appended when a key is seen again?",
        ],
        hints=[
            "Use a dictionary from anagram signature to a list of words.",
            "A tuple of 26 character counts avoids sorting each word.",
            "Create the group on the first occurrence of a signature.",
            "Return the dictionary's group lists in insertion order.",
        ],
        tests=[
            {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]], "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
            {"args": [[""]], "expected": [[""]]},
            {"args": [["a", "a"]], "expected": [["a", "a"]]},
            {"args": [[]], "expected": []},
        ],
    ),
    _problem(
        id="top-k-frequent",
        title="Top K Frequent Elements",
        difficulty="Medium",
        tags=["Arrays", "Hash Map", "Heap"],
        summary="Return the k most frequent values using deterministic tie-breaking.",
        description=(
            "Given an integer list and an integer `k`, return the `k` values with the highest occurrence counts. "
            "Order the result by decreasing frequency; when two values have the same frequency, place the smaller "
            "numeric value first. The input is guaranteed to contain at least `k` distinct values."
        ),
        signature="def solve(nums, k):",
        examples=[
            ("nums = [1,1,1,2,2,3], k = 2", "[1, 2]", "`1` occurs three times and `2` occurs twice."),
            ("nums = [4,4,5,5,6], k = 2", "[4, 5]", "`4` and `5` tie, so the smaller value comes first."),
            ("nums = [7], k = 1", "[7]", "The only distinct value is the most frequent."),
        ],
        constraints=["1 <= len(nums) <= 100,000", "1 <= k <= number of distinct values.", "Sort by frequency descending, then value ascending."],
        guide=[
            "What first pass provides the frequency of each distinct value?",
            "How can the required tie-breaking be expressed as a sort key?",
            "When would a heap be preferable to sorting all distinct values?",
            "What portion of the ranked values should be returned?",
        ],
        hints=[
            "Build a frequency dictionary.",
            "Sort distinct values using key `(-frequency[value], value)`.",
            "Take the first `k` values from that ordering.",
            "A size-`k` heap is an alternative for very large numbers of distinct values.",
        ],
        tests=[
            {"args": [[1,1,1,2,2,3], 2], "expected": [1, 2]},
            {"args": [[4,4,5,5,6], 2], "expected": [4, 5]},
            {"args": [[7], 1], "expected": [7]},
            {"args": [[-1,-1,2,2,3], 2], "expected": [-1, 2]},
        ],
    ),
    _problem(
        id="three-sum",
        title="Three Sum",
        difficulty="Medium",
        tags=["Arrays", "Two Pointers", "Sorting"],
        summary="Find every unique triplet whose values sum to zero.",
        description=(
            "Return all unique triplets `[a, b, c]` selected from distinct indices such that `a + b + c = 0`. "
            "Sort each triplet in ascending order and return the triplets in lexicographic order. Duplicate input "
            "values may exist, but duplicate triplets must not appear in the output."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [-1,0,1,2,-1,-4]", "[[-1,-1,2],[-1,0,1]]", "These are the two distinct value combinations summing to zero."),
            ("nums = [0,1,1]", "[]", "No three selected values sum to zero."),
            ("nums = [0,0,0,0]", "[[0,0,0]]", "Repeated zeroes produce one unique triplet."),
        ],
        constraints=["0 <= len(nums) <= 3,000", "Use distinct indices.", "Return unique sorted triplets in lexicographic order."],
        guide=[
            "How does sorting enable a two-pointer search for each fixed first value?",
            "When the current sum is too small or too large, which pointer should move?",
            "Where must duplicate fixed values be skipped?",
            "After finding a triplet, how can duplicate second and third values be avoided?",
        ],
        hints=[
            "Sort the input first.",
            "Fix index `i`, then search the suffix using left and right pointers.",
            "Move left for a sum below zero and right for a sum above zero.",
            "Skip equal adjacent values at every selection level.",
        ],
        tests=[
            {"args": [[-1,0,1,2,-1,-4]], "expected": [[-1,-1,2],[-1,0,1]]},
            {"args": [[0,1,1]], "expected": []},
            {"args": [[0,0,0,0]], "expected": [[0,0,0]]},
            {"args": [[-2,0,1,1,2]], "expected": [[-2,0,2],[-2,1,1]]},
        ],
    ),
    _problem(
        id="container-most-water",
        title="Container With Most Water",
        difficulty="Medium",
        tags=["Arrays", "Two Pointers", "Greedy"],
        summary="Choose two vertical lines that contain the greatest area.",
        description=(
            "Each `height[i]` is the height of a vertical line at horizontal position `i`. Choose two lines to form "
            "a container with the x-axis and return the maximum water area. The area is the distance between the "
            "indices multiplied by the shorter of the two heights; lines may not be tilted."
        ),
        signature="def solve(height):",
        examples=[
            ("height = [1,8,6,2,5,4,8,3,7]", "49", "Indices `1` and `8` give width `7` and limiting height `7`."),
            ("height = [1,1]", "1", "The only pair has width `1` and height `1`."),
            ("height = [4,3,2,1,4]", "16", "The two height-`4` lines are four positions apart."),
        ],
        constraints=["2 <= len(height) <= 100,000", "Heights are non-negative integers."],
        guide=[
            "Why is the current area limited by the shorter boundary?",
            "After evaluating the widest pair, which pointer can move without discarding a better possibility?",
            "Why can moving the taller boundary not improve the limiting height?",
            "What information must be updated at every pointer configuration?",
        ],
        hints=[
            "Start with pointers at the two ends.",
            "Compute `width * min(left_height, right_height)`.",
            "Move the pointer at the shorter line inward.",
            "Track the maximum area seen before the pointers meet.",
        ],
        tests=[
            {"args": [[1,8,6,2,5,4,8,3,7]], "expected": 49},
            {"args": [[1,1]], "expected": 1},
            {"args": [[4,3,2,1,4]], "expected": 16},
            {"args": [[1,2,1]], "expected": 2},
        ],
    ),
    _problem(
        id="minimum-size-subarray-sum",
        title="Minimum Size Subarray Sum",
        difficulty="Medium",
        tags=["Arrays", "Sliding Window"],
        summary="Find the shortest positive-number window whose sum reaches a target.",
        description=(
            "Given a positive integer `target` and a list of positive integers `nums`, return the minimum length "
            "of a contiguous subarray whose sum is at least `target`. Return `0` when no such subarray exists. "
            "The positivity of all values allows the window to shrink greedily."
        ),
        signature="def solve(target, nums):",
        examples=[
            ("target = 7, nums = [2,3,1,2,4,3]", "2", "The subarray `[4,3]` reaches `7` with length `2`."),
            ("target = 4, nums = [1,4,4]", "1", "A single `4` already reaches the target."),
            ("target = 11, nums = [1,1,1,1,1,1,1,1]", "0", "Even the entire array sums to less than `11`."),
        ],
        constraints=["1 <= target", "0 <= len(nums) <= 100,000", "Every value in `nums` is positive."],
        guide=[
            "What does the current window sum represent?",
            "When should the right boundary expand?",
            "Once the sum reaches the target, why is it safe to shrink from the left repeatedly?",
            "How should the result represent the case where no valid window is found?",
        ],
        hints=[
            "Add each new right-boundary value to a running sum.",
            "While the sum is at least the target, record the length and remove the left value.",
            "Positive values ensure removing from the left is the only way to seek a shorter window.",
            "Use infinity as an initial best length and convert it to zero at the end.",
        ],
        tests=[
            {"args": [7, [2,3,1,2,4,3]], "expected": 2},
            {"args": [4, [1,4,4]], "expected": 1},
            {"args": [11, [1,1,1,1,1,1,1,1]], "expected": 0},
            {"args": [15, [1,2,3,4,5]], "expected": 5},
        ],
    ),
    _problem(
        id="character-replacement",
        title="Longest Repeating Character Replacement",
        difficulty="Medium",
        tags=["Strings", "Sliding Window", "Hash Map"],
        summary="Maximize a same-character substring after at most k replacements.",
        description=(
            "Given an uppercase string `s` and integer `k`, you may replace at most `k` characters with any "
            "uppercase letter. Return the maximum length of a substring that can be made entirely one repeated "
            "character. The chosen substring must be contiguous."
        ),
        signature="def solve(s, k):",
        examples=[
            ("s = 'ABAB', k = 2", "4", "Replace both `A` values or both `B` values to make all four characters equal."),
            ("s = 'AABABBA', k = 1", "4", "A length-four window such as `AABA` can be made all `A`."),
            ("s = 'AAAA', k = 0", "4", "No replacements are needed."),
        ],
        constraints=["0 <= len(s) <= 100,000", "0 <= k <= len(s)", "The string contains uppercase English letters."],
        guide=[
            "Within a window, how many characters must be replaced to make all characters equal?",
            "Which frequency inside the window determines that replacement count?",
            "When does the window become invalid and require shrinking?",
            "Why can the maximum observed character frequency be maintained without decreasing it?",
        ],
        hints=[
            "For a window of length `L`, replacements needed are `L - max_frequency`.",
            "Expand the right boundary and update character counts.",
            "Shrink while `window_length - max_frequency > k`.",
            "Track the largest valid window length.",
        ],
        tests=[
            {"args": ["ABAB", 2], "expected": 4},
            {"args": ["AABABBA", 1], "expected": 4},
            {"args": ["AAAA", 0], "expected": 4},
            {"args": ["ABCDE", 1], "expected": 2},
        ],
    ),
    _problem(
        id="daily-temperatures",
        title="Daily Temperatures",
        difficulty="Medium",
        tags=["Arrays", "Monotonic Stack"],
        summary="For each day, count how long until a warmer temperature occurs.",
        description=(
            "For every index in `temperatures`, return the number of days until a strictly warmer temperature. "
            "Return `0` when no warmer future day exists. Equal temperatures are not warmer, and a quadratic "
            "forward scan should be avoided."
        ),
        signature="def solve(temperatures):",
        examples=[
            ("temperatures = [73,74,75,71,69,72,76,73]", "[1,1,4,2,1,1,0,0]", "The `75` at index `2` waits four days for `76`."),
            ("temperatures = [30,40,50,60]", "[1,1,1,0]", "Each day except the last is followed immediately by a warmer day."),
            ("temperatures = [30,30,30]", "[0,0,0]", "Equal future temperatures do not count as warmer."),
        ],
        constraints=["0 <= len(temperatures) <= 100,000", "A future temperature must be strictly greater."],
        guide=[
            "Which unresolved days should remain on the stack?",
            "What ordering property should their temperatures have?",
            "When the current temperature is warmer than the stack top, what answer becomes known?",
            "Why is each index pushed and popped at most once?",
        ],
        hints=[
            "Store indices, not temperatures alone, on the stack.",
            "Keep the stack monotonic decreasing by temperature.",
            "Pop while the current temperature is greater than the temperature at the top index.",
            "For a popped index, the wait is `current_index - popped_index`.",
        ],
        tests=[
            {"args": [[73,74,75,71,69,72,76,73]], "expected": [1,1,4,2,1,1,0,0]},
            {"args": [[30,40,50,60]], "expected": [1,1,1,0]},
            {"args": [[30,30,30]], "expected": [0,0,0]},
            {"args": [[]], "expected": []},
        ],
    ),
    _problem(
        id="evaluate-rpn",
        title="Evaluate Reverse Polish Notation",
        difficulty="Medium",
        tags=["Stack", "Math"],
        summary="Evaluate an arithmetic expression written in postfix notation.",
        description=(
            "Tokens form a valid Reverse Polish Notation expression using integers and the operators `+`, `-`, "
            "`*`, and `/`. When an operator appears, apply it to the two most recent values, preserving left and "
            "right operand order. Integer division must truncate toward zero, not toward negative infinity."
        ),
        signature="def solve(tokens):",
        examples=[
            ("tokens = ['2','1','+','3','*']", "9", "`(2 + 1) * 3 = 9`."),
            ("tokens = ['4','13','5','/','+']", "6", "`13 / 5` truncates to `2`, then `4 + 2 = 6`."),
            ("tokens = ['7','-3','/']", "-2", "`7 / -3` truncates toward zero to `-2`."),
        ],
        constraints=["1 <= len(tokens) <= 10,000", "The expression is valid.", "Division truncates toward zero."],
        guide=[
            "What should happen when a numeric token is encountered?",
            "Which two stack values belong to an operator, and in what order?",
            "Why is subtraction or division sensitive to pop order?",
            "How can Python division be converted to truncation toward zero?",
        ],
        hints=[
            "Push integers onto a stack.",
            "For an operator, pop the right operand first and the left operand second.",
            "Push the computed result back onto the stack.",
            "Use `int(left / right)` for truncation toward zero.",
        ],
        tests=[
            {"args": [["2","1","+","3","*"]], "expected": 9},
            {"args": [["4","13","5","/","+"]], "expected": 6},
            {"args": [["7","-3","/"]], "expected": -2},
            {"args": [["10","6","9","3","+","-11","*","/","*","17","+","5","+"]], "expected": 22},
        ],
    ),
    _problem(
        id="search-rotated-array",
        title="Search in Rotated Sorted Array",
        difficulty="Medium",
        tags=["Arrays", "Binary Search"],
        summary="Find a target in a sorted array rotated at an unknown pivot.",
        description=(
            "The distinct integers in `nums` were originally sorted in ascending order, then rotated at an unknown "
            "position. Return the index of `target`, or `-1` when absent. At every binary-search step, at least one "
            "half of the current interval remains normally sorted; use that fact to choose the next half."
        ),
        signature="def solve(nums, target):",
        examples=[
            ("nums = [4,5,6,7,0,1,2], target = 0", "4", "The target appears after the rotation pivot at index `4`."),
            ("nums = [4,5,6,7,0,1,2], target = 3", "-1", "The target is absent."),
            ("nums = [1], target = 1", "0", "A one-element rotated array is still searchable."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "Values are distinct.", "Target `O(log n)` time."],
        guide=[
            "How can you identify whether the left or right half is normally sorted?",
            "If the left half is sorted, how do you test whether the target lies inside it?",
            "How does the decision change when the right half is sorted?",
            "Which inclusive boundaries and loop condition avoid missing endpoints?",
        ],
        hints=[
            "Use ordinary binary-search boundaries.",
            "If `nums[left] <= nums[mid]`, the left half is sorted.",
            "Check whether the target falls within the sorted half's value range.",
            "Search the opposite half when the target is outside that range.",
        ],
        tests=[
            {"args": [[4,5,6,7,0,1,2], 0], "expected": 4},
            {"args": [[4,5,6,7,0,1,2], 3], "expected": -1},
            {"args": [[1], 1], "expected": 0},
            {"args": [[3,1], 1], "expected": 1},
            {"args": [[], 2], "expected": -1},
        ],
    ),
    _problem(
        id="first-last-position",
        title="Find First and Last Position",
        difficulty="Medium",
        tags=["Arrays", "Binary Search"],
        summary="Locate the complete index range occupied by a target in a sorted list.",
        description=(
            "Given a nondecreasing integer list that may contain duplicates, return `[first, last]`, the first and "
            "last indices where `target` appears. Return `[-1, -1]` when the target is absent. The required running "
            "time is logarithmic, so a linear expansion from one found occurrence is not sufficient."
        ),
        signature="def solve(nums, target):",
        examples=[
            ("nums = [5,7,7,8,8,10], target = 8", "[3, 4]", "The two `8` values occupy indices `3` through `4`."),
            ("nums = [5,7,7,8,8,10], target = 6", "[-1, -1]", "The target does not occur."),
            ("nums = [2,2,2], target = 2", "[0, 2]", "The target spans the entire list."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "The input is sorted in nondecreasing order.", "Target `O(log n)` time."],
        guide=[
            "How can binary search be modified to continue left after finding the target?",
            "What symmetric change finds the rightmost occurrence?",
            "Can a reusable boundary-search helper express both searches?",
            "How should absence be detected before returning a range?",
        ],
        hints=[
            "Run one binary search for the first occurrence.",
            "After finding a match in the first search, save it and move `right` leftward.",
            "Run a second search that saves matches and moves `left` rightward.",
            "Return `[-1, -1]` if the first occurrence was never found.",
        ],
        tests=[
            {"args": [[5,7,7,8,8,10], 8], "expected": [3,4]},
            {"args": [[5,7,7,8,8,10], 6], "expected": [-1,-1]},
            {"args": [[2,2,2], 2], "expected": [0,2]},
            {"args": [[], 0], "expected": [-1,-1]},
            {"args": [[1], 1], "expected": [0,0]},
        ],
    ),
    _problem(
        id="koko-bananas",
        title="Koko Eating Bananas",
        difficulty="Medium",
        tags=["Binary Search", "Math"],
        summary="Find the minimum integer eating speed that meets a deadline.",
        description=(
            "Each value in `piles` is a pile of bananas. At an integer speed `k`, one hour is spent on one pile and "
            "up to `k` bananas are eaten from it; unfinished piles require additional hours. Return the smallest speed "
            "that finishes all piles within `h` hours. Search over possible speeds rather than simulating every speed."
        ),
        signature="def solve(piles, h):",
        examples=[
            ("piles = [3,6,7,11], h = 8", "4", "At speed `4`, the piles require `1 + 2 + 2 + 3 = 8` hours."),
            ("piles = [30,11,23,4,20], h = 5", "30", "Only one hour is available per pile, so the largest pile size is required."),
            ("piles = [30,11,23,4,20], h = 6", "23", "Speed `23` finishes within six hours, while `22` does not."),
        ],
        constraints=["1 <= len(piles) <= 100,000", "h >= len(piles)", "Speed is a positive integer."],
        guide=[
            "What are the smallest and largest speeds worth considering?",
            "How many hours does a pile of size p require at speed k?",
            "Is feasibility monotonic as the speed increases?",
            "When a speed is feasible, which half may still contain a better answer?",
        ],
        hints=[
            "Binary-search speeds from `1` through `max(piles)`.",
            "Hours for one pile are ceiling division: `(pile + speed - 1) // speed`.",
            "A feasible speed means all larger speeds are also feasible.",
            "On feasibility, save the candidate and search lower speeds.",
        ],
        tests=[
            {"args": [[3,6,7,11], 8], "expected": 4},
            {"args": [[30,11,23,4,20], 5], "expected": 30},
            {"args": [[30,11,23,4,20], 6], "expected": 23},
            {"args": [[1,1,1,1], 8], "expected": 1},
        ],
    ),
    _problem(
        id="merge-intervals",
        title="Merge Intervals",
        difficulty="Medium",
        tags=["Intervals", "Sorting"],
        summary="Combine all overlapping closed intervals.",
        description=(
            "Each interval is `[start, end]` with `start <= end`. Merge intervals that overlap or touch at an endpoint, "
            "and return a sorted list of disjoint intervals covering the same values. For example, `[1,4]` and `[4,5]` "
            "must merge because closed intervals share the point `4`."
        ),
        signature="def solve(intervals):",
        examples=[
            ("intervals = [[1,3],[2,6],[8,10],[15,18]]", "[[1,6],[8,10],[15,18]]", "The first two intervals overlap and combine."),
            ("intervals = [[1,4],[4,5]]", "[[1,5]]", "Touching closed intervals merge at endpoint `4`."),
            ("intervals = []", "[]", "There are no intervals to merge."),
        ],
        constraints=["0 <= len(intervals) <= 100,000", "Each interval has two integers with start <= end.", "Return intervals sorted by start."],
        guide=[
            "Why should intervals be sorted by their start values first?",
            "What condition determines whether the next interval overlaps the current merged interval?",
            "How should the merged end value be updated?",
            "When must a completed interval be appended to the result?",
        ],
        hints=[
            "Sort intervals by start.",
            "Compare the next start with the end of the last merged interval.",
            "On overlap, replace the last end with the larger end.",
            "Otherwise append a new interval to the result.",
        ],
        tests=[
            {"args": [[[1,3],[2,6],[8,10],[15,18]]], "expected": [[1,6],[8,10],[15,18]]},
            {"args": [[[1,4],[4,5]]], "expected": [[1,5]]},
            {"args": [[]], "expected": []},
            {"args": [[[1,10],[2,3],[4,8]]], "expected": [[1,10]]},
        ],
    ),
    _problem(
        id="insert-interval",
        title="Insert Interval",
        difficulty="Medium",
        tags=["Intervals", "Greedy"],
        summary="Insert one interval into a sorted disjoint interval list and merge as needed.",
        description=(
            "`intervals` is already sorted by start and contains no overlapping intervals. Insert `new_interval`, "
            "merge every overlap or endpoint touch it creates, and return the resulting sorted disjoint list. Preserve "
            "intervals that lie completely before or completely after the merged insertion."
        ),
        signature="def solve(intervals, new_interval):",
        examples=[
            ("intervals = [[1,3],[6,9]], new_interval = [2,5]", "[[1,5],[6,9]]", "The new interval overlaps `[1,3]` and extends it to `5`."),
            ("intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], new_interval = [4,8]", "[[1,2],[3,10],[12,16]]", "The insertion connects four middle intervals into one."),
            ("intervals = [], new_interval = [5,7]", "[[5,7]]", "The insertion becomes the only interval."),
        ],
        constraints=["0 <= len(intervals) <= 100,000", "Existing intervals are sorted and disjoint.", "Closed intervals that touch must merge."],
        guide=[
            "Which intervals can be copied directly because they end before the insertion begins?",
            "Which intervals overlap the evolving insertion and must be absorbed?",
            "How do the insertion's start and end change during merging?",
            "What remains after the merged insertion is appended?",
        ],
        hints=[
            "First append intervals whose end is less than the new start.",
            "While the next start is at most the current new end, merge it.",
            "Update with the minimum start and maximum end.",
            "Append the merged insertion, then append all remaining intervals.",
        ],
        tests=[
            {"args": [[[1,3],[6,9]], [2,5]], "expected": [[1,5],[6,9]]},
            {"args": [[[1,2],[3,5],[6,7],[8,10],[12,16]], [4,8]], "expected": [[1,2],[3,10],[12,16]]},
            {"args": [[], [5,7]], "expected": [[5,7]]},
            {"args": [[[1,2],[5,6]], [3,4]], "expected": [[1,2],[3,4],[5,6]]},
        ],
    ),
    _problem(
        id="spiral-matrix",
        title="Spiral Matrix",
        difficulty="Medium",
        tags=["Matrix", "Simulation"],
        summary="Return matrix values in clockwise spiral order.",
        description=(
            "Starting at the top-left corner, traverse a rectangular matrix clockwise: across the top row, down the "
            "right column, across the bottom row in reverse, and up the left column. Continue inward layer by layer "
            "until every cell has been returned exactly once."
        ),
        signature="def solve(matrix):",
        examples=[
            ("matrix = [[1,2,3],[4,5,6],[7,8,9]]", "[1,2,3,6,9,8,7,4,5]", "The outer ring is visited first, followed by the center."),
            ("matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]", "[1,2,3,4,8,12,11,10,9,5,6,7]", "The traversal continues into the remaining inner row."),
            ("matrix = []", "[]", "An empty matrix has no traversal values."),
        ],
        constraints=["0 <= rows, cols <= 200", "Rows have equal length.", "Return each cell exactly once."],
        guide=[
            "Which four boundaries describe the remaining unvisited rectangle?",
            "How does each directional traversal change one boundary?",
            "Why are boundary checks needed before traversing the bottom row and left column?",
            "What condition means no unvisited rectangle remains?",
        ],
        hints=[
            "Maintain `top`, `bottom`, `left`, and `right` boundaries.",
            "Traverse one side, then move its boundary inward.",
            "Before traversing backward sides, confirm the boundaries have not crossed.",
            "Continue while `top <= bottom` and `left <= right`.",
        ],
        tests=[
            {"args": [[[1,2,3],[4,5,6],[7,8,9]]], "expected": [1,2,3,6,9,8,7,4,5]},
            {"args": [[[1,2,3,4],[5,6,7,8],[9,10,11,12]]], "expected": [1,2,3,4,8,12,11,10,9,5,6,7]},
            {"args": [[]], "expected": []},
            {"args": [[[1],[2],[3]]], "expected": [1,2,3]},
        ],
    ),
    _problem(
        id="rotate-matrix",
        title="Rotate Matrix 90 Degrees",
        difficulty="Medium",
        tags=["Matrix"],
        summary="Return a square matrix rotated clockwise by ninety degrees.",
        description=(
            "Given an `n x n` matrix, return a new matrix representing a 90-degree clockwise rotation. An element "
            "originally at row `r`, column `c` moves to row `c`, column `n - 1 - r`. The original input does not need "
            "to be modified in place."
        ),
        signature="def solve(matrix):",
        examples=[
            ("matrix = [[1,2,3],[4,5,6],[7,8,9]]", "[[7,4,1],[8,5,2],[9,6,3]]", "The first column becomes the first row in reverse order."),
            ("matrix = [[1,2],[3,4]]", "[[3,1],[4,2]]", "Each original coordinate is mapped to its clockwise position."),
            ("matrix = [[5]]", "[[5]]", "A one-cell matrix is unchanged by rotation."),
        ],
        constraints=["1 <= n <= 300", "The matrix is square.", "Return a new rotated matrix."],
        guide=[
            "What coordinate mapping describes a clockwise rotation?",
            "How does transposing and then reversing each row produce the same result?",
            "Which dimensions should the output matrix have?",
            "How can all positions be filled without overwriting needed input values?",
        ],
        hints=[
            "For each input cell `(r, c)`, write it to `(c, n - 1 - r)`.",
            "Initialize an `n x n` output matrix first.",
            "A compact alternative is transpose followed by reversing every row.",
            "Return the new matrix after every cell is mapped.",
        ],
        tests=[
            {"args": [[[1,2,3],[4,5,6],[7,8,9]]], "expected": [[7,4,1],[8,5,2],[9,6,3]]},
            {"args": [[[1,2],[3,4]]], "expected": [[3,1],[4,2]]},
            {"args": [[[5]]], "expected": [[5]]},
            {"args": [[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]], "expected": [[13,9,5,1],[14,10,6,2],[15,11,7,3],[16,12,8,4]]},
        ],
    ),
    _problem(
        id="set-matrix-zeroes",
        title="Set Matrix Zeroes",
        difficulty="Medium",
        tags=["Matrix", "Hash Set"],
        summary="Zero every row and column containing an original zero.",
        description=(
            "If any original matrix cell equals zero, every cell in that cell's row and column must become zero. "
            "Return the transformed matrix. Decisions must be based on the original zero positions; newly written "
            "zeroes must not trigger additional rows or columns."
        ),
        signature="def solve(matrix):",
        examples=[
            ("matrix = [[1,1,1],[1,0,1],[1,1,1]]", "[[1,0,1],[0,0,0],[1,0,1]]", "The middle row and middle column are zeroed."),
            ("matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]", "[[0,0,0,0],[0,4,5,0],[0,3,1,0]]", "Rows and columns containing either original zero are cleared."),
            ("matrix = [[1,2],[3,4]]", "[[1,2],[3,4]]", "Without an original zero, the matrix is unchanged."),
        ],
        constraints=["1 <= rows, cols <= 300", "Rows have equal length.", "Return the transformed matrix."],
        guide=[
            "Why would immediately zeroing cells during discovery create incorrect cascading changes?",
            "What row and column information should be recorded during the first pass?",
            "How can the second pass decide whether each cell becomes zero?",
            "What constant-space marker optimization is possible using the first row and column?",
        ],
        hints=[
            "First collect the indices of rows and columns containing original zeroes.",
            "Do not modify other cells until discovery is complete.",
            "In a second pass, zero a cell when its row or column is marked.",
            "Using sets is clear and acceptable for this version.",
        ],
        tests=[
            {"args": [[[1,1,1],[1,0,1],[1,1,1]]], "expected": [[1,0,1],[0,0,0],[1,0,1]]},
            {"args": [[[0,1,2,0],[3,4,5,2],[1,3,1,5]]], "expected": [[0,0,0,0],[0,4,5,0],[0,3,1,0]]},
            {"args": [[[1,2],[3,4]]], "expected": [[1,2],[3,4]]},
            {"args": [[[0]]], "expected": [[0]]},
        ],
    ),
    _problem(
        id="number-of-islands",
        title="Number of Islands",
        difficulty="Medium",
        tags=["Matrix", "Graph Traversal", "BFS/DFS"],
        summary="Count four-directionally connected land components in a grid.",
        description=(
            "The grid contains strings `'1'` for land and `'0'` for water. An island is a maximal group of land cells "
            "connected through up, down, left, or right moves. Return the number of distinct islands. Diagonal land "
            "cells belong to different islands unless another four-directional path connects them."
        ),
        signature="def solve(grid):",
        examples=[
            ("grid = [['1','1','1'],['0','1','0'],['1','0','1']]", "3", "The top region and the two isolated bottom corners form three islands."),
            ("grid = [['1','1'],['1','1']]", "1", "All four land cells are connected."),
            ("grid = [['0','0'],['0','0']]", "0", "The grid contains no land."),
        ],
        constraints=["0 <= rows, cols <= 300", "Cells are `'0'` or `'1'`.", "Connectivity is four-directional."],
        guide=[
            "What event indicates that a newly discovered island has been found?",
            "How can traversal mark every cell belonging to that island?",
            "What prevents the same land cell from being counted again?",
            "How does the outer grid scan interact with DFS or BFS?",
        ],
        hints=[
            "Scan every cell in the grid.",
            "When an unvisited land cell is found, increment the island count.",
            "Run DFS or BFS to visit all connected land cells.",
            "Mark visited cells in a set or change copied land cells to water.",
        ],
        tests=[
            {"args": [[['1','1','1'],['0','1','0'],['1','0','1']]], "expected": 3},
            {"args": [[['1','1'],['1','1']]], "expected": 1},
            {"args": [[['0','0'],['0','0']]], "expected": 0},
            {"args": [[]], "expected": 0},
            {"args": [[['1','0','1'],['0','1','0'],['1','0','1']]], "expected": 5},
        ],
    ),
    _problem(
        id="course-schedule",
        title="Course Schedule",
        difficulty="Medium",
        tags=["Graphs", "Topological Sort", "BFS/DFS"],
        summary="Determine whether all courses can be completed without prerequisite cycles.",
        description=(
            "Courses are numbered from `0` through `num_courses - 1`. Each pair `[course, prerequisite]` means the "
            "prerequisite must be completed before the course. Return `True` if a valid completion order exists for "
            "all courses, or `False` if the dependency graph contains a directed cycle."
        ),
        signature="def solve(num_courses, prerequisites):",
        examples=[
            ("num_courses = 2, prerequisites = [[1,0]]", "True", "Complete course `0` before course `1`."),
            ("num_courses = 2, prerequisites = [[1,0],[0,1]]", "False", "Each course requires the other, creating a cycle."),
            ("num_courses = 4, prerequisites = [[1,0],[2,1],[3,2]]", "True", "The chain `0,1,2,3` is a valid order."),
        ],
        constraints=["1 <= num_courses <= 100,000", "Course identifiers are valid.", "Duplicate prerequisite pairs may be treated as one dependency."],
        guide=[
            "How should each prerequisite pair be represented as a directed edge?",
            "What does the indegree of a course represent?",
            "Which courses can be processed immediately in Kahn's algorithm?",
            "How does the processed-course count reveal whether a cycle remains?",
        ],
        hints=[
            "Build edges from prerequisite to dependent course.",
            "Count the indegree of every course.",
            "Start a queue with all zero-indegree courses and remove their outgoing edges.",
            "All courses are completable only if the number processed equals `num_courses`.",
        ],
        tests=[
            {"args": [2, [[1,0]]], "expected": True},
            {"args": [2, [[1,0],[0,1]]], "expected": False},
            {"args": [4, [[1,0],[2,1],[3,2]]], "expected": True},
            {"args": [3, []], "expected": True},
            {"args": [3, [[1,0],[2,1],[0,2]]], "expected": False},
        ],
    ),
    _problem(
        id="shortest-unweighted-path",
        title="Shortest Path in an Unweighted Graph",
        difficulty="Medium",
        tags=["Graphs", "BFS"],
        summary="Find the minimum number of edges between two nodes.",
        description=(
            "An undirected graph has nodes `0` through `n - 1` and edges listed as `[u, v]`. Return the minimum "
            "number of edges on any path from `start` to `end`. Return `0` when the endpoints are the same and `-1` "
            "when the destination is unreachable. Because every edge has equal cost, breadth-first search is appropriate."
        ),
        signature="def solve(n, edges, start, end):",
        examples=[
            ("n = 5, edges = [[0,1],[1,2],[0,3],[3,4],[4,2]], start = 0, end = 2", "2", "The path `0 -> 1 -> 2` uses two edges."),
            ("n = 4, edges = [[0,1],[2,3]], start = 0, end = 3", "-1", "The endpoints belong to different connected components."),
            ("n = 3, edges = [[0,1]], start = 2, end = 2", "0", "No edge is needed to remain at the starting node."),
        ],
        constraints=["1 <= n <= 100,000", "Edges are undirected.", "Node identifiers and endpoints are valid."],
        guide=[
            "How should an undirected edge be added to an adjacency list?",
            "Why does BFS discover nodes in nondecreasing path length?",
            "What information should accompany each queued node?",
            "When can the search stop early?",
        ],
        hints=[
            "Add both `u -> v` and `v -> u` to the adjacency list.",
            "Use a queue containing `(node, distance)` pairs.",
            "Mark a node visited when it is enqueued.",
            "Return the distance as soon as the destination is reached.",
        ],
        tests=[
            {"args": [5, [[0,1],[1,2],[0,3],[3,4],[4,2]], 0, 2], "expected": 2},
            {"args": [4, [[0,1],[2,3]], 0, 3], "expected": -1},
            {"args": [3, [[0,1]], 2, 2], "expected": 0},
            {"args": [6, [[0,1],[1,2],[2,3],[0,4],[4,5],[5,3]], 0, 3], "expected": 3},
        ],
    ),
    _problem(
        id="coin-change",
        title="Coin Change",
        difficulty="Medium",
        tags=["Dynamic Programming"],
        summary="Find the minimum number of coins needed to form an amount.",
        description=(
            "You have unlimited copies of every positive denomination in `coins`. Return the fewest coins whose values "
            "sum exactly to `amount`, or `-1` when the amount cannot be formed. Coin order does not matter, and the "
            "same denomination may be used multiple times."
        ),
        signature="def solve(coins, amount):",
        examples=[
            ("coins = [1,2,5], amount = 11", "3", "The minimum is `5 + 5 + 1`."),
            ("coins = [2], amount = 3", "-1", "No combination of value-`2` coins forms `3`."),
            ("coins = [2,3], amount = 0", "0", "No coins are needed to form zero."),
        ],
        constraints=["0 <= amount <= 100,000", "Coin values are positive.", "Unlimited copies of each denomination are available."],
        guide=[
            "What should `dp[x]` represent for each partial amount x?",
            "How can a coin transition from a smaller amount to x?",
            "What sentinel value distinguishes an amount not yet reachable?",
            "Which base state represents forming amount zero?",
        ],
        hints=[
            "Let `dp[x]` be the minimum coins needed for amount `x`.",
            "Initialize `dp[0] = 0` and other entries to an unreachable sentinel.",
            "For each amount and coin, consider `dp[amount - coin] + 1`.",
            "Return `-1` if the target entry remains unreachable.",
        ],
        tests=[
            {"args": [[1,2,5], 11], "expected": 3},
            {"args": [[2], 3], "expected": -1},
            {"args": [[2,3], 0], "expected": 0},
            {"args": [[2,5,10,1], 27], "expected": 4},
            {"args": [[3,7], 5], "expected": -1},
        ],
    ),
    _problem(
        id="house-robber",
        title="House Robber",
        difficulty="Medium",
        tags=["Arrays", "Dynamic Programming"],
        summary="Maximize collected value without choosing adjacent positions.",
        description=(
            "Each value in `nums` is the money stored in a house along one street. You may choose any houses, but "
            "choosing two adjacent houses is forbidden. Return the maximum total amount that can be collected. You "
            "may choose no houses when the list is empty."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [1,2,3,1]", "4", "Choose houses with values `1` and `3`."),
            ("nums = [2,7,9,3,1]", "12", "Choose values `2`, `9`, and `1`."),
            ("nums = []", "0", "There is nothing to collect."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "House values are non-negative integers."],
        guide=[
            "At each house, what are the two choices?",
            "If the current house is chosen, which previous optimum can be combined with it?",
            "If it is skipped, which previous optimum remains?",
            "Why are only two previous states needed?",
        ],
        hints=[
            "Track the best totals through the previous house and the house before it.",
            "The new best is `max(previous_best, two_back + current_value)`.",
            "Shift the two state variables after each house.",
            "Initialize both states to zero.",
        ],
        tests=[
            {"args": [[1,2,3,1]], "expected": 4},
            {"args": [[2,7,9,3,1]], "expected": 12},
            {"args": [[]], "expected": 0},
            {"args": [[5]], "expected": 5},
            {"args": [[2,1,1,2]], "expected": 4},
        ],
    ),
    _problem(
        id="decode-ways",
        title="Decode Ways",
        difficulty="Medium",
        tags=["Strings", "Dynamic Programming"],
        summary="Count valid letter decodings of a digit string.",
        description=(
            "Digits map to letters as `1 -> A` through `26 -> Z`. Given a nonempty digit string `s`, return the number "
            "of complete decodings. A standalone `0` is invalid, but it may appear as part of `10` or `20`. Leading "
            "zeroes therefore make the entire string undecodable."
        ),
        signature="def solve(s):",
        examples=[
            ("s = '12'", "2", "The decodings are `AB` and `L`."),
            ("s = '226'", "3", "The decodings are `BZ`, `VF`, and `BBF`."),
            ("s = '06'", "0", "A decoding cannot begin with zero."),
        ],
        constraints=["1 <= len(s) <= 100,000", "The string contains digits only.", "Only values `1` through `26` map to letters."],
        guide=[
            "What does the number of decodings for a prefix depend on?",
            "When can the current single digit extend every decoding of the previous prefix?",
            "When can the final two digits form one valid letter?",
            "How do zero digits affect each transition?",
        ],
        hints=[
            "Use dynamic programming over prefix lengths.",
            "A nonzero current digit contributes the previous prefix count.",
            "A two-digit number from `10` through `26` contributes the count from two positions back.",
            "Return zero immediately for a leading zero, or let the transitions naturally produce zero.",
        ],
        tests=[
            {"args": ["12"], "expected": 2},
            {"args": ["226"], "expected": 3},
            {"args": ["06"], "expected": 0},
            {"args": ["10"], "expected": 1},
            {"args": ["11106"], "expected": 2},
        ],
    ),
    _problem(
        id="longest-increasing-subsequence",
        title="Longest Increasing Subsequence",
        difficulty="Medium",
        tags=["Arrays", "Binary Search", "Dynamic Programming"],
        summary="Find the length of the longest strictly increasing subsequence.",
        description=(
            "A subsequence keeps the original order but may skip elements. Return the maximum length of a strictly "
            "increasing subsequence in `nums`; equal adjacent chosen values do not count as increasing. Aim for an "
            "`O(n log n)` solution by maintaining efficient candidate tails."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [10,9,2,5,3,7,101,18]", "4", "One longest subsequence is `[2,3,7,101]`."),
            ("nums = [0,1,0,3,2,3]", "4", "A valid longest subsequence is `[0,1,2,3]`."),
            ("nums = [7,7,7,7]", "1", "Equal values cannot extend a strictly increasing subsequence."),
        ],
        constraints=["0 <= len(nums) <= 100,000", "The subsequence must be strictly increasing.", "Target `O(n log n)` time."],
        guide=[
            "What does `tails[length - 1]` represent in the patience-sorting approach?",
            "Where should a new value replace an existing tail?",
            "Why does a smaller tail preserve more future extension possibilities?",
            "When does the tails list grow?",
        ],
        hints=[
            "Maintain the smallest possible tail value for every subsequence length.",
            "Use binary search for the first tail greater than or equal to the current value.",
            "Replace that tail, or append when no such tail exists.",
            "The final tails length is the answer, though tails itself may not be an actual subsequence.",
        ],
        tests=[
            {"args": [[10,9,2,5,3,7,101,18]], "expected": 4},
            {"args": [[0,1,0,3,2,3]], "expected": 4},
            {"args": [[7,7,7,7]], "expected": 1},
            {"args": [[]], "expected": 0},
            {"args": [[4,10,4,3,8,9]], "expected": 3},
        ],
    ),
    _problem(
        id="word-break",
        title="Word Break",
        difficulty="Medium",
        tags=["Strings", "Dynamic Programming", "Hash Set"],
        summary="Determine whether a string can be segmented into dictionary words.",
        description=(
            "Given a string `s` and a list of reusable dictionary words, return `True` if `s` can be split into one "
            "or more dictionary words in sequence. Every character must belong to exactly one chosen word. Dictionary "
            "words may be used multiple times."
        ),
        signature="def solve(s, words):",
        examples=[
            ("s = 'leetcode', words = ['leet','code']", "True", "Split the string as `leet | code`."),
            ("s = 'applepenapple', words = ['apple','pen']", "True", "The word `apple` is reused."),
            ("s = 'catsandog', words = ['cats','dog','sand','and','cat']", "False", "No sequence of dictionary words covers the entire string."),
        ],
        constraints=["0 <= len(s) <= 10,000", "Dictionary words are nonempty.", "Words may be reused."],
        guide=[
            "What should `dp[i]` mean for the prefix ending before index i?",
            "How can a valid earlier split be extended by one dictionary word?",
            "Why is storing dictionary words in a set useful?",
            "How can maximum word length reduce unnecessary substring checks?",
        ],
        hints=[
            "Let `dp[i]` indicate whether `s[:i]` can be segmented.",
            "Initialize `dp[0] = True` for the empty prefix.",
            "For each endpoint, search for an earlier valid split whose intervening substring is a dictionary word.",
            "Return `dp[len(s)]`.",
        ],
        tests=[
            {"args": ["leetcode", ["leet","code"]], "expected": True},
            {"args": ["applepenapple", ["apple","pen"]], "expected": True},
            {"args": ["catsandog", ["cats","dog","sand","and","cat"]], "expected": False},
            {"args": ["", ["a"]], "expected": True},
            {"args": ["aaaaaaa", ["aaaa","aaa"]], "expected": True},
        ],
    ),
    _problem(
        id="combination-sum",
        title="Combination Sum",
        difficulty="Medium",
        tags=["Backtracking", "Arrays"],
        summary="Find unique reusable-number combinations that reach a target sum.",
        description=(
            "`candidates` contains distinct positive integers, and each value may be selected any number of times. "
            "Return every unique combination whose sum equals `target`. Values inside each combination must be in "
            "nondecreasing order, and the list of combinations must be lexicographically ordered."
        ),
        signature="def solve(candidates, target):",
        examples=[
            ("candidates = [2,3,6,7], target = 7", "[[2,2,3],[7]]", "Either reuse `2` twice with `3`, or choose `7`."),
            ("candidates = [2,3,5], target = 8", "[[2,2,2,2],[2,3,3],[3,5]]", "These are all unique nondecreasing combinations."),
            ("candidates = [2], target = 1", "[]", "No positive combination can sum to `1`."),
        ],
        constraints=["1 <= len(candidates) <= 30", "Candidate values are distinct and positive.", "A candidate may be reused.", "Return canonical ordered output."],
        guide=[
            "How does sorting candidates help produce canonical combinations and enable pruning?",
            "What state describes a backtracking call?",
            "Why should recursive calls continue from the current candidate index rather than zero?",
            "When can the loop stop because all later candidates are too large?",
        ],
        hints=[
            "Sort candidates first.",
            "Track the remaining target, current path, and minimum allowed candidate index.",
            "Recurse with the same index to permit reuse.",
            "Record a copy of the path when the remaining target reaches zero.",
        ],
        tests=[
            {"args": [[2,3,6,7], 7], "expected": [[2,2,3],[7]]},
            {"args": [[2,3,5], 8], "expected": [[2,2,2,2],[2,3,3],[3,5]]},
            {"args": [[2], 1], "expected": []},
            {"args": [[8,7,4,3], 11], "expected": [[3,4,4],[3,8],[4,7]]},
        ],
    ),
    _problem(
        id="permutations",
        title="Permutations",
        difficulty="Medium",
        tags=["Backtracking", "Arrays"],
        summary="Generate every ordering of a list of distinct values.",
        description=(
            "Given a list of distinct integers, return every possible permutation. Each permutation must contain every "
            "input value exactly once. Return the permutations in lexicographic order, which can be achieved by exploring "
            "available values in sorted order."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [1,2,3]", "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]", "There are `3! = 6` complete orderings."),
            ("nums = [0,1]", "[[0,1],[1,0]]", "Two distinct values have two permutations."),
            ("nums = [5]", "[[5]]", "A one-element list has one permutation."),
        ],
        constraints=["0 <= len(nums) <= 8", "All values are distinct.", "Return permutations in lexicographic order."],
        guide=[
            "What does the current path represent during backtracking?",
            "How can the algorithm know which values are still available?",
            "When is a path complete and ready to record?",
            "Why should candidate values be considered in sorted order?",
        ],
        hints=[
            "Sort the input before beginning.",
            "Track used indices or pass a list of remaining values.",
            "Choose one unused value, recurse, then undo the choice.",
            "Append a copy when the path length equals the input length.",
        ],
        tests=[
            {"args": [[1,2,3]], "expected": [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]},
            {"args": [[0,1]], "expected": [[0,1],[1,0]]},
            {"args": [[5]], "expected": [[5]]},
            {"args": [[]], "expected": [[]]},
            {"args": [[2,1]], "expected": [[1,2],[2,1]]},
        ],
    ),
    _problem(
        id="generate-parentheses",
        title="Generate Parentheses",
        difficulty="Medium",
        tags=["Backtracking", "Strings"],
        summary="Generate all balanced strings containing n parenthesis pairs.",
        description=(
            "Given `n`, return every well-formed string containing exactly `n` opening and `n` closing parentheses. "
            "At no prefix may closing parentheses outnumber opening parentheses. Return results in lexicographic order; "
            "exploring an opening parenthesis before a closing parenthesis naturally produces that order."
        ),
        signature="def solve(n):",
        examples=[
            ("n = 3", "['((()))','(()())','(())()','()(())','()()()']", "These are all five balanced arrangements of three pairs."),
            ("n = 1", "['()']", "Only one balanced arrangement exists."),
            ("n = 0", "['']", "The empty string is the single balanced arrangement of zero pairs."),
        ],
        constraints=["0 <= n <= 8", "Return every valid string exactly once in lexicographic order."],
        guide=[
            "What two counters describe how many opening and closing parentheses have been used?",
            "When is adding an opening parenthesis legal?",
            "When is adding a closing parenthesis legal without invalidating the prefix?",
            "What condition marks a complete valid string?",
        ],
        hints=[
            "Track `open_used` and `close_used`.",
            "Add `(` while `open_used < n`.",
            "Add `)` only while `close_used < open_used`.",
            "Record the string when its length reaches `2 * n`.",
        ],
        tests=[
            {"args": [3], "expected": ["((()))","(()())","(())()","()(())","()()()"]},
            {"args": [1], "expected": ["()"]},
            {"args": [0], "expected": [""]},
            {"args": [2], "expected": ["(())","()()"]},
        ],
    ),
    _problem(
        id="subsets",
        title="Subsets",
        difficulty="Medium",
        tags=["Backtracking", "Arrays"],
        summary="Generate the complete power set of a list of distinct values.",
        description=(
            "Given a list of distinct integers, return every subset, including the empty subset and the full list. "
            "Each input value may appear at most once in a subset. Sort values inside each subset, then order the "
            "complete result first by subset length and then lexicographically among subsets of equal length."
        ),
        signature="def solve(nums):",
        examples=[
            ("nums = [1,2,3]", "[[],[1],[2],[3],[1,2],[1,3],[2,3],[1,2,3]]", "The three-value set has `2^3 = 8` subsets."),
            ("nums = [0]", "[[],[0]]", "The subsets are the empty set and the set containing `0`."),
            ("nums = []", "[[]]", "The empty input has one subset: the empty subset."),
        ],
        constraints=["0 <= len(nums) <= 15", "All values are distinct.", "Return subsets ordered by length, then lexicographically."],
        guide=[
            "For each value, what two choices create the subset decision tree?",
            "How can an increasing start index prevent duplicate subset construction?",
            "At what point during backtracking should the current subset be recorded?",
            "What final ordering step enforces the required length-first output contract?",
        ],
        hints=[
            "Sort the input first so values inside subsets are ordered.",
            "Record a copy of the current path at every backtracking call.",
            "Choose each candidate from the current start index onward, recurse, then undo the choice.",
            "Sort the collected subsets using key `(len(subset), subset)` before returning.",
        ],
        tests=[
            {"args": [[1,2,3]], "expected": [[],[1],[2],[3],[1,2],[1,3],[2,3],[1,2,3]]},
            {"args": [[0]], "expected": [[],[0]]},
            {"args": [[]], "expected": [[]]},
            {"args": [[2,1]], "expected": [[],[1],[2],[1,2]]},
        ],
    ),
]

_IMPORTED_CATALOG_PATH = Path(__file__).with_name("imported_problems.json")
if _IMPORTED_CATALOG_PATH.exists():
    _imported_problems = json.loads(_IMPORTED_CATALOG_PATH.read_text(encoding="utf-8"))
    _known_titles = {problem["title"].casefold() for problem in PROBLEMS}
    PROBLEMS.extend(
        problem
        for problem in _imported_problems
        if problem["title"].casefold() not in _known_titles
    )

PROBLEM_BY_ID = {problem["id"]: problem for problem in PROBLEMS}
