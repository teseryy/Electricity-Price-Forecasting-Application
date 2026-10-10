FROM python:3.10

WORKDIR /code

COPY . /code/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD pytest --maxfail=1 --disable-warnings --tb=short && fastapi run app/main.py --port 8010