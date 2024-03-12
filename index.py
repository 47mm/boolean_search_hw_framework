from collections import Counter
from typing import Iterable


class Tokenizer:
    def tokenize(self, doc: str) -> Iterable[str]:
        return doc.split()


class IndexMemory:
    def __init__(self) -> None:
        self._inverted_index: dict[str, list[int]] = {}
        self._docnum = 0
        self._docnum_to_docid: dict[int, str] = {}
        self._tokenizer = Tokenizer()
        self.token_occurences = Counter()
        self.total_token_occur = 0

    def add_document(self, doc: str, docid: str):
        tokens = self._tokenizer.tokenize(doc)
        for token in tokens:
            self.token_occurences[token] += 1
            postings = self._inverted_index.setdefault(token, [])
            if not postings or postings[-1] != self._docnum:
                postings.append(self._docnum)
        self._docnum_to_docid[self._docnum] = docid
        self._docnum += 1

    def commit(self):
        self.total_token_occur = self.token_occurences.total()

    def postings(self, token: str) -> list[int]:
        return self._inverted_index.get(token, [])

    def has_token(self, token: str) -> bool:
        return token in self._inverted_index

    def get_docid(self, docnum: int):
        return self._docnum_to_docid[docnum]

    def language_model(self, token: str):
        '''Probability of `word`. Naive implementation.'''
        assert self.token_occurences != 0
        return self.token_occurences[token] / self.total_token_occur
