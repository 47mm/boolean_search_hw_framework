#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import re

import numpy as np
from natasha import (Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc)

import pandas as pd
from tqdm import tqdm


class Index:
    def __init__(self, index_file):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(emb)
        self.inverted_index = {}
        with open(index_file) as file:
            for line in tqdm(file, desc='Creating Index...'):
                first_tab = line.find('\t')
                doc_id = int(line[1:first_tab])
                text = self._preproccess_line(line[first_tab + 2:])
                for word in text:
                    if word in self.inverted_index:
                        self.inverted_index[word].add(doc_id)
                    else:
                        self.inverted_index[word] = {doc_id}
        # with open('saved_dictionary.pkl', 'wb') as f:
        #    pickle.dump(self.inverted_index, f)

        # with open('saved_dictionary.pkl', 'rb') as f:
        #    self.inverted_index = pickle.load(f)

    def _preproccess_line(self, line):
        s = re.sub(r'[^A-ZА-Я0-9 ]', '', line)
        doc = Doc(s)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
        tokens = []
        for token in doc.tokens:
            tokens.append(token.lemma.upper())
        return tokens

    def get_index(self):
        return self.inverted_index


class QueryTree:
    def __init__(self, qid, query):
        self.qid = qid
        self.query = query
        self.result = None
        self.reversed_index = None
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(emb)

    def _preproccess_line(self, line):
        s = re.sub(r'[^A-ZА-Я0-9 ]', '', line)
        doc = Doc(s)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
        tokens = []
        for token in doc.tokens:
            tokens.append(token.lemma.upper())
        return ''.join(tokens)

    def search(self, index):
        self.reversed_index = index.get_index()
        return self.qid, self._S()

    def _is_brackets(self, q):
        if q[0] != '(':
            return False
        brackets = 0
        for c in q[1:-1]:
            if c == '(':
                brackets += 1
            if c == ')':
                brackets -= 1
            if brackets < 0:
                return False
        return brackets == 0

    def _remove_brackets(self, q):
        return q[1:-1]

    def _is_primitive(self, q):
        return not('|' in q or ' ' in q or '(' in q or ')' in q)

    def _get_next_lexem(self, query, is_and_block):
        q = ''
        bracket_block = 0
        for c in query:
            q += c
            if c == ' ' and bracket_block == 0 and is_and_block:
                q1 = q[:-1]
                q = ''
                yield q1
            if c == '|' and bracket_block == 0 and not is_and_block:
                q1 = q[:-1]
                q = ''
                yield q1
            if c == '(':
                bracket_block += 1
                continue
            if bracket_block and c != ')':
                continue
            if c == ')':
                bracket_block -= 1
                continue
        yield q

    def _is_and_block(self, query):
        bracket_block = 0
        for c in query:
            if c == '|' and bracket_block == 0:
                return False
            if c == '(':
                bracket_block += 1
                continue
            if c == ')':
                bracket_block -= 1
        return True

    def _add_results(self, result, postings, is_and_block):
        if is_and_block:
            result = result & postings if result is not None else postings
        else:
            result = result | postings if result is not None else postings
        return result

    def _or_and_block(self, sequence, is_and_block):
        result = None

        for q in self._get_next_lexem(sequence, is_and_block):
            if self._is_brackets(q):
                q = self._remove_brackets(q)
            if self._is_primitive(q):
                q1 = self._preproccess_line(q)
                postings = self.reversed_index.get(q1, set())
                result = self._add_results(result, postings, is_and_block)
                continue

            postings = self._or_and_block(q, self._is_and_block(q))
            result = self._add_results(result, postings, is_and_block)
        return result

    def _S(self):
        result = self._or_and_block(self.query, True)
        return result



class SearchResults:
    def __init__(self):
        self.results = {}

    def add(self, found):
        qid, result = found
        self.results[qid] = found

    def print_submission(self, objects_file, submission_file):
        df = pd.read_csv(objects_file)
        ans = []
        for qid in df['QueryId'].unique():
            find = self.results[qid][1]
            ans.extend(df[df['QueryId'] == qid]['DocumentId'].str[1:].astype(int).isin(find).astype(int).values)
        ans = pd.DataFrame({
            'ObjectId': 1 + np.arange(len(ans)),
            'Relevance': ans,
        })
        ans.to_csv(submission_file, index=False)


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    parser.add_argument('--queries_file', required=True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required=True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required=True, help='docs.tsv')
    parser.add_argument('--submission_file', required=True, help='output file with relevances')
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file)

    # Process queries.
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for line in tqdm(queries_fh, desc='Processing queries...'):
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]
            # Parse query.
            query_tree = QueryTree(qid, query)
            # Search and save results.
            search_results.add(query_tree.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
