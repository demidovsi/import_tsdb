FROM python:3.9

COPY . /code

WORKDIR /code

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]