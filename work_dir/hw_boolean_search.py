#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import re

import numpy as np
from natasha import (Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc)
import nltk
nltk.download('stopwords')
import pandas as pd
from tqdm import tqdm
import pickle


class Index:
    def __init__(self, index_file):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(emb)
        self.parts_of_speech = ['PROPN', 'ADJ', 'NOUN', 'X', 'VERB', 'NUM']
        self.stop_words = nltk.corpus.stopwords.words('russian') + nltk.corpus.stopwords.words('english')
        self.inverted_index = {}
        with open(index_file) as file:
            for line in tqdm(file, desc='Creating Index'):
                first_tab = line.find('\t')
                doc_id = int(line[1:first_tab])
                text = self._preproccess_line(line[first_tab + 2:])
                for word in text:
                    if word in self.inverted_index:
                        self.inverted_index[word].add(doc_id)
                    else:
                        self.inverted_index[word] = {doc_id}
        with open('saved_dictionary.pkl', 'wb') as f:
            pickle.dump(self.inverted_index, f)
        # with open('saved_dictionary.pkl', 'rb') as f:
        #   self.inverted_index = pickle.load(f)

    def _preproccess_line(self, line):
        s = re.sub(r'[^A-ZА-Я0-9 ]', '', line)
        doc = Doc(s)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
        tokens = []
        for token in doc.tokens:
            if token.pos in self.parts_of_speech and token.lemma not in self.stop_words:
                tokens.append(token.text)
        return tokens

    def get_index(self):
        return self.inverted_index


class QueryTree:
    def __init__(self, qid, query):
        self.qid = qid
        self.query = query

    def search(self, index):
        reversed_index = index.get_index()
        print( self.qid, self._split(self.query, reversed_index))
        return self.qid, self._split(self.query, reversed_index)

    def _split(self, query, reversed_index):
        results = None
        bracket_block = 0
        or_block = False
        q = ''
        for c in query:
            q += c
            if c == '(':
                bracket_block += 1
                continue
            if bracket_block and c != ')':
                continue
            if c == ')':
                bracket_block -= 1
                if bracket_block == 0:
                    postings = self._split(q[1:-1], reversed_index)
                    results = results & postings if results is not None else postings
                    q = ''
                continue
            if c == '|' and not bracket_block:
                if q[:-1]:
                    postings = self._split(q[:-1], reversed_index)
                    results = results | postings if results is not None else postings
                    or_block = True
                q = ''
            if c == ' ' and not bracket_block and not or_block:
                if q.strip():
                    postings = self._split(q[:-1], reversed_index)
                    results = results & postings if results is not None else postings
                q = ''
                continue
            if c == ' ':
                if not q.strip():
                    or_block = False
                    q = ''
                continue
        q = q.strip()
        if ' ' in q:
            for q_and in q.split(' '):
                postings = reversed_index.get(q_and, set())
                if or_block:
                    results = results | postings if results is not None else postings
                else:
                    results = results & postings if results is not None else postings
        else:
            if q:
                postings = reversed_index.get(q, set())
                if or_block:
                    results = results | postings if results is not None else postings
                else:
                    results = results & postings if results is not None else postings
        return results


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
        for line in queries_fh:
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
