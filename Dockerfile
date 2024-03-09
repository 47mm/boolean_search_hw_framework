FROM python:3.12-alpine

WORKDIR /usr/src/app

COPY work_dir ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "hw_boolean_search.py", "--queries_file", "data/queries.numerate.txt", "--objects_file",  "data/objects.numerate.txt", "--docs_file", "data/docs.txt", "--submission_file", "output.csv"]