#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
from typing import Iterable
from time import perf_counter

from index import IndexMemory
from searcher import Searcher




def create_and_fill_memory_index(docs_filepath):
    print('Start creating memory index...')
    start = perf_counter()
    index = IndexMemory()
    with open(docs_filepath) as f:
        for i, line in enumerate(f, 1):
            fields = line.rstrip('\n').split('\t')
            docid, title, body = fields
            doc = title + ' ' + body
            index.add_document(doc, docid)
            if i % 1000 == 0:
                print(f"Processed {i} documents")
    index.commit()
    print(f'Memory index created, total time: {perf_counter() - start}')
    return index



INDEX_DIR = 'indexdir'


class SearchResults:
    def __init__(self):
        self._qid_to_docids: dict[int, set] = {}

    def add(self, qid: int, docids: Iterable[str]):
        self._qid_to_docids[qid] = set(docids)

    def print_submission(self, objects_file, submission_file):
        obj_file = open(objects_file)
        obj_file_iter = iter(obj_file)
        next(obj_file_iter)

        subm_file = open(submission_file, 'w')
        subm_file.write('ObjectId,Relevance\n')

        for line in obj_file_iter:
            obj_id, qid, docid = line.rstrip('\n').split(',')
            qid = int(qid)
            if docid in self._qid_to_docids[qid]:
                finded = 1
            else:
                finded = 0
            subm_file.write(f'{obj_id},{finded}\n')


def main():
    # Command line argum_indexents.
    parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    parser.add_argument('--queries_file', required = True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required = True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required = True, help='docs.tsv')
    parser.add_argument('--submission_file', required = True, help='output file with relevances')
    args = parser.parse_args()

    index = create_and_fill_memory_index(args.docs_file)

    # Searcher
    searcher = Searcher(index, top_k=30)

    # Process queries.
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for i, line in enumerate(queries_fh, 1):
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]

            result_docids = searcher.search(query)
            search_results.add(qid, result_docids)
            if i % 100 == 0:
                print(f'Processed {i} queries')

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
