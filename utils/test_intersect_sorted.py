import unittest
from search_framework.utils.for_sorted import intersect_sorted_unique


class TestIntersect(unittest.TestCase):
    def test_normal(self):
        lst1 = [1, 2]
        lst2 = [2, 3]
        result = [2]
        self.assertEqual(intersect_sorted_unique(lst1, lst2), result)

    def test_different_len(self):
        cases = [
            {
                "fst": [1, 2, 3, 4, 5],
                "snd": [2, 5],
                "result": [2, 5]
            },
            {
                "fst": [1, 6],
                "snd": [1, 4, 5, 6],
                "result": [1, 6]
            },
            {
                "fst": [1, 2],
                "snd": [2, 4, 7],
                "result": [2]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(intersect_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_empty(self):
        cases = [
            {
                "fst": [1, 2],
                "snd": [],
                "result": []
            },
            {
                "fst": [],
                "snd": [3, 4],
                "result": []
            },
            {
                "fst": [],
                "snd": [],
                "result": []
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(intersect_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_one_elem(self):
        cases = [
            {
                "fst": [1],
                "snd": [1, 4],
                "result": [1]
            },
            {
                "fst": [1, 2],
                "snd": [2],
                "result": [2]
            },
            {
                "fst": [1],
                "snd": [4],
                "result": []
            },
            {
                "fst": [5],
                "snd": [5],
                "result": [5]
            }
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(intersect_sorted_unique(tc["fst"], tc["snd"]), tc["result"])

    def test_some(self):
        cases = [
            {
                "fst": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "snd": [2, 4, 6, 8, 10, 11, 12, 13],
                "result": [2, 4, 6, 8, 10]
            },
            {
                "fst": [2, 4, 6, 8, 10, 11, 12, 13],
                "snd": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "result": [2, 4, 6, 8, 10]
            },
        ]
        for i, tc in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(intersect_sorted_unique(tc["fst"], tc["snd"]), tc["result"])