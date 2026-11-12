# Built-in DSA problem bank for the coding round.
# Each test is [arguments, expected result]. Results are compared as JSON values.

PROBLEMS = {
    "two-sum": {
        "title": "Two Sum",
        "difficulty": "Easy",
        "function": "two_sum",
        "compare": "sorted",
        "statement": (
            "Given a list of integers nums and an integer target, return the indices of the two "
            "numbers that add up to target. Exactly one solution exists, and you may not use the "
            "same element twice. You can return the indices in any order."
        ),
        "example": "two_sum([2, 7, 11, 15], 9)  ->  [0, 1]",
        "starter": "def two_sum(nums, target):\n    # write your solution here\n    pass\n",
        "tests": [
            [[[2, 7, 11, 15], 9], [0, 1]],
            [[[3, 2, 4], 6], [1, 2]],
            [[[3, 3], 6], [0, 1]],
            [[[-1, -2, -3, -4, -5], -8], [2, 4]],
            [[[0, 4, 3, 0], 0], [0, 3]],
            [[[1, 5, 9, 2], 10], [0, 2]],
            [[list(range(20000)), 39997], [19998, 19999]],
        ],
        "hints": [
            "Think about what you need to find for each number. If you are at x, which other value would complete the target?",
            "Checking every pair works but is slow for large lists. What could you remember about the numbers you have already seen?",
            "A dictionary that maps each value to its index lets you check in one step whether the complement was seen earlier.",
        ],
    },
    "valid-parentheses": {
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "function": "is_valid",
        "compare": "exact",
        "statement": (
            "Given a string s made only of the characters ( ) [ ] { }, decide whether it is valid. "
            "A string is valid if every opening bracket is closed by the same type of bracket, "
            "and brackets are closed in the correct order."
        ),
        "example": "is_valid('()[]{}')  ->  True        is_valid('(]')  ->  False",
        "starter": "def is_valid(s):\n    # write your solution here\n    pass\n",
        "tests": [
            [["()"], True],
            [["()[]{}"], True],
            [["(]"], False],
            [["([)]"], False],
            [["{[]}"], True],
            [[""], True],
            [["(("], False],
            [["]"], False],
        ],
        "hints": [
            "The most recent opening bracket must be the first one to be closed. Which structure behaves that way?",
            "A stack: push each opening bracket, and when you see a closing bracket, compare it with the top of the stack.",
            "Remember the two failure cases: a closing bracket with an empty stack, and brackets left on the stack at the end.",
        ],
    },
    "max-subarray": {
        "title": "Maximum Subarray",
        "difficulty": "Medium",
        "function": "max_subarray",
        "compare": "exact",
        "statement": (
            "Given a list of integers nums, find the contiguous sub-list (at least one element) "
            "with the largest sum, and return that sum."
        ),
        "example": "max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])  ->  6",
        "starter": "def max_subarray(nums):\n    # write your solution here\n    pass\n",
        "tests": [
            [[[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 6],
            [[[1]], 1],
            [[[5, 4, -1, 7, 8]], 23],
            [[[-3, -2, -1]], -1],
            [[[-2, -1]], -1],
            [[[2, -1, 2, -1, 2]], 4],
            [[[1] * 200000], 200000],
        ],
        "hints": [
            "Walk through the list once. At each position, what is the best sum of a sub-list that ends right here?",
            "Either extend the previous best sub-list, or start fresh at this element. Take whichever is larger.",
            "Keep two numbers: the best sum ending here, and the best sum seen so far. Be careful when every number is negative.",
        ],
    },
    "merge-intervals": {
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "function": "merge",
        "compare": "exact",
        "statement": (
            "Given a list of intervals where intervals[i] = [start, end], merge all overlapping "
            "intervals and return the non-overlapping intervals that cover the same ranges, "
            "sorted by start. Intervals that touch at a point, such as [1, 4] and [4, 5], overlap."
        ),
        "example": "merge([[1, 3], [2, 6], [8, 10]])  ->  [[1, 6], [8, 10]]",
        "starter": "def merge(intervals):\n    # write your solution here\n    pass\n",
        "tests": [
            [[[[1, 3], [2, 6], [8, 10], [15, 18]]], [[1, 6], [8, 10], [15, 18]]],
            [[[[1, 4], [4, 5]]], [[1, 5]]],
            [[[[1, 4], [0, 4]]], [[0, 4]]],
            [[[[1, 4], [2, 3]]], [[1, 4]]],
            [[[[5, 6], [1, 2]]], [[1, 2], [5, 6]]],
            [[[]], []],
        ],
        "hints": [
            "The order of the input is not guaranteed. What would make overlapping intervals sit next to each other?",
            "Sort by start. Then compare each interval with the last interval you kept.",
            "If the next start is at most the last end, merge by taking the larger of the two ends. Otherwise start a new interval.",
        ],
    },
    "longest-substring": {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "function": "length_of_longest_substring",
        "compare": "exact",
        "statement": (
            "Given a string s, return the length of the longest substring that contains no "
            "repeated character."
        ),
        "example": "length_of_longest_substring('abcabcbb')  ->  3",
        "starter": "def length_of_longest_substring(s):\n    # write your solution here\n    pass\n",
        "tests": [
            [["abcabcbb"], 3],
            [["bbbbb"], 1],
            [["pwwkew"], 3],
            [[""], 0],
            [[" "], 1],
            [["dvdf"], 3],
            [["abba"], 2],
            [["ab" * 50000], 2],
        ],
        "hints": [
            "Think of a window over the string that you can grow on the right and shrink on the left.",
            "When the new character is already inside the window, move the left edge past its earlier position.",
            "Store the last index of each character in a dictionary, and only ever move the left edge forward (watch the case 'abba').",
        ],
    },
}