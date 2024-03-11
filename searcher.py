import heapq

from index import IndexMemory
# from search_framework.index.in_memory.index import IndexMemory
from utils.for_sorted import (
    merge_sorted_unique,
    merge_sorted_unique_many,
    intersect_sorted_unique,
)
from typing import Iterable
from heapq import nlargest


class Searcher:
    # TODO: TEST
    def __init__(self, index: IndexMemory, top_k_for_exsisting = 3, top_k = 10):
        self._index = index
        self._service_symbols = {"(", ")", " ", "|"}
        self._op_priority = {"(": 0, "|": 1, " ": 2}
        self._rpn_operators = {' ', '|'}
        self.top_k = top_k
        self.top_k_for_exsisting = top_k_for_exsisting

    def search(self, query: str) -> list[str]:
        """
        Return doc_ids list for query
        """
        parsed = self._parse_query(query)
        rpn = self._to_rpn(parsed)
        postings = self._execute_rpn(rpn)

        doc_ids = [''] * len(postings)
        for i, docnum in enumerate(postings):
            doc_ids[i] = self._index.get_docid(docnum)
        return doc_ids

    def _parse_query(self, query: str) -> list[str]:
        """
        Convert string query to list of items (token or operator)
        """
        query_list = []
        word = []
        for ch in query:
            if ch in self._service_symbols:
                if word:
                    query_list.append(''.join(word))
                    word = []
                query_list.append(ch)
            else:
                word.append(ch)
        if word:
            query_list.append(''.join(word))
        return query_list

    def _to_rpn(self, query: list[str]) -> list[str]:
        """
        Convert parsed query to Reverse Polish Notation
        """
        bracket_cnt = 0
        result: list[str] = []
        stack = []
        for w in query:
            if w == "(":
                stack.append(w)
                bracket_cnt += 1
            elif w == ")":
                bracket_cnt -= 1
                if bracket_cnt < 0:
                    raise ValueError("wrong brackets")
                while stack and stack[-1] != "(":
                    result.append(stack.pop())
                stack.pop()
            elif w in self._op_priority:
                while stack and self._op_priority[stack[-1]] >= self._op_priority[w]:
                    result.append(stack.pop())
                stack.append(w)
            else:
                result.append(w)
        if bracket_cnt != 0:
            raise ValueError("wrong brackets")
        while stack:
            result.append(stack.pop())
        return result

    def  _execute_rpn(self, query: list[str]) -> list[int]:
        """
        Return postings list
        """
        stack: list[list[int]] = []
        for w in query:
            if w in self._rpn_operators:
                if len(stack) < 2:
                    raise ValueError("bad query")
                snd, fst = stack.pop(), stack.pop()
                if w == ' ':
                    result = intersect_sorted_unique(fst, snd)
                else:
                    result = merge_sorted_unique(fst, snd)
                stack.append(result)
            else:
                edited = {w}
                if len(w) >= 2:
                    edited |= edits1(w)
                edited = self._limit_candidates(edited)

                layouted = change_layout(w)
                lay_edited = {layouted}
                if len(layouted) >= 3:
                    edited |= self._limit_candidates(edits1(layouted))
                edited |= self._limit_candidates(lay_edited)
                edited = self._get_top_k(edited, top_k=self.top_k)

                postings = merge_sorted_unique_many(
                    [self._index.postings(token) for token in edited]
                )
                stack.append(postings)
        result = stack.pop()
        if stack:
            raise ValueError("bad query")
        return result

    def _limit_candidates(self, tokens: Iterable[str]) -> set[str]:
        '''The subset of `tokens` that appear in the dictionary of words_occurences.'''
        output = set()
        for token in tokens:
            if self._index.has_token(token):
                output.add(token)
        return output

    def _get_top_k(self, words: Iterable[str], top_k: int) -> list[str]:
        return nlargest(top_k, words, self._index.language_model)


def all_edits1(words: set[str]) -> set[str]:
    output = set()
    for w in words:
        output |= edits1(w)
    return output


def edits1(word: str) -> set[str]:
    '''All edits that are one edit away from `word`.'''
    if is_rus(word):
        letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    else:
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits]
    transposes = [L[:-1] + R[0] + L[-1] + R[1:] for L, R in splits if len(L) > 0 and len(R) > 0]
    replaces = []
    for c in letters:
        replaces += [L + c + R[1:] for L, R in splits]
    inserts = []
    for c in letters:
        inserts += [L + c + R for L, R in splits]
    # prefixes = [L for L, _ in splits if len(L) >= 3]
    # suffixes = [R for _, R in splits if len(R) >= 3]
    return set(deletes + transposes + replaces + inserts)


def edits2(word: str) -> set[str]:
    '''All edits that are 2 edits away from `word`.'''
    output = set()
    for candidate in edits1(word):
        output.update(edits1(candidate))
    return output


ENG = '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''
RUS = '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''


def layout_eng_2_rus(text):
    layout = dict(zip(map(ord, ENG), RUS))
    return text.translate(layout)


def layout_rus_2_eng(text):
    layout = dict(zip(map(ord, RUS), ENG))
    return text.translate(layout)


def change_layout(word: str) -> str:
    if is_rus(word):
        return layout_rus_2_eng(word)
    return layout_eng_2_rus(word)


def is_rus(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
    return not alphabet.isdisjoint(text.lower())
