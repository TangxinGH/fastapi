# fastapi-example [![CircleCI](https://circleci.com/gh/marciovrl/fastapi-example.svg?style=svg)](https://circleci.com/gh/marciovrl/fastapi-example)

A simple example of using Fast API in Python.

## Preconditions:

- Python 3

## Clone the project

```
git clone https://github.com/marciovrl/fastapi-example.git
```

## Run local

### Install dependencies

```
pip install -r requirements.txt
```

### Run server

```
uvicorn app.main:app --reload
```

### Run test

```
pytest app/test.py
```

## Run with docker

### Run server

```
docker-compose up -d --build
```

### Run test

```
docker-compose exec app pytest test/test.py
```

## API documentation (provided by Swagger UI)

```
http://127.0.0.1:8000/docs
```

### Run server

```
docker-compose exec db psql --username=fastapi --dbname=fastapi_dev
```
sqlacodegen sqlite:///fast.db  --outfile app/model/dbmodels.py
{"AppKey":"d","EventCode":"456","EventName":"helloworld "}
--onefile --hidden-import=main main.py

https://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html
nc -zvu

pyinstaller -w -F app\main.py -i dist\file.png -n Service.tsx
auto create db