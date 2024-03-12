import unittest
from search_framework.utils.for_sorted import merge_sorted_unique, merge_sorted_unique_many


class TestMergeUnique(unittest.TestCase):
    def test_normal(self):
        lst1 = [1, 2]
        lst2 = [3, 4]
        result = [1, 2, 3, 4]
        self.assertEqual(merge_sorted_unique(lst1, lst2), result)

    def test_different_len(self):
        cases = [
            {
                "fst": [1, 2, 3, 4, 5],
                "snd": [6, 7],
                "result": [1, 2, 3, 4, 5, 6, 7]
            },
            {
                "fst": [1, 2],
                "snd": [3, 4, 5, 6],
                "result": [1, 2, 3, 4, 5, 6]
            },
            {
                "fst": [1, 2],
                "snd": [3, 6, 7],
                "result": [1, 2, 3, 6, 7]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_empty(self):
        cases = [
            {
                "fst": [1, 2],
                "snd": [],
                "result": [1, 2]
            },
            {
                "fst": [],
                "snd": [3, 4],
                "result": [3, 4]
            },
            {
                "fst": [],
                "snd": [],
                "result": []
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_one_elem(self):
        cases = [
            {
                "fst": [1],
                "snd": [3, 4],
                "result": [1, 3, 4]
            },
            {
                "fst": [1, 2],
                "snd": [4],
                "result": [1, 2, 4]
            },
            {
                "fst": [1],
                "snd": [4],
                "result": [1, 4]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_inverse(self):
        cases = [
            {
                "fst": [3, 4, 5],
                "snd": [1, 2],
                "result": [1, 2, 3, 4, 5]
            },
            {
                "fst": [3],
                "snd": [1],
                "result": [1, 3]
            },
            {
                "fst": [4, 5],
                "snd": [1],
                "result": [1, 4, 5]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_some(self):
        cases = [
            {
                "fst": [1, 3, 5, 7],
                "snd": [2, 4, 6, 8, 10],
                "result": [1, 2, 3, 4, 5, 6, 7, 8, 10]
            },
            {
                "fst": [2, 4, 6, 8, 10],
                "snd": [1, 3, 5, 7],
                "result":[1, 2, 3, 4, 5, 6, 7, 8, 10]
            },
            {
                "fst": [1, 3, 5, 7, 9],
                "snd": [2, 4, 6, 8, 10],
                "result": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_only_unique(self):
        cases = [
            {
                "fst": [1, 2],
                "snd": [2, 3],
                "result": [1, 2, 3]
            },
            {
                "fst": [1, 2, 3, 4],
                "snd": [2, 3, 4, 5, 6],
                "result": [1, 2, 3, 4, 5, 6]
            },
            {
                "fst": [1, 2, 3, 5, 6],
                "snd": [3, 4, 5],
                "result": [1, 2, 3, 4, 5, 6]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(merge_sorted_unique(tc["fst"], tc["snd"]), tc["result"])


class TestMergeSortedMany(unittest.TestCase):
    def test_normal(self):
        lst = [
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
            [6, 7, 8],
        ]
        result = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertEqual(
            merge_sorted_unique_many(lst),
            result
        )