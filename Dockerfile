FROM python:3.9-alpine

COPY . /code

WORKDIR /code

RUN pip install --no--cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
