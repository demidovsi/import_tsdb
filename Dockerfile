FROM python:3.9-alpine

COPY . /code

WORKDIR /code

RUN pip install -r requirements.txt --no--cache-dir

CMD [ "python", "./main.py" ]