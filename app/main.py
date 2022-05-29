import os

# from fastapi_sqlalchemy import DBSessionMiddleware
os.environ['sqlalchemy_url'] = "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')

import time
from multiprocessing import Process

import fastapi_sqla
import uvicorn
from apscheduler.schedulers.twisted import TwistedScheduler
from fastapi import FastAPI, HTTPException
from loguru import logger
# from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.responses import Response
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from app.api import api
from app.db.models import UserAnswer

app = FastAPI()
# app.add_middleware(DBSessionMiddleware, db_url="sqlite:///" + os.path.join(os.getcwd(), 'app', 'db', 'fast.db'))
fastapi_sqla.setup(app)
sched = TwistedScheduler()
sched.start()


class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        self.transport.write(datagram, address)
        print(datagram)
        print("sleep3")
        sched.add_job(func=api.event_record_json, args=(datagram, address))
        # msg, sock = datagram
        resp = time.ctime()
        self.transport.write(resp.encode('ascii'), address)


@app.post("/event")
def root():
    return api.event_record()


@app.get("/")
def root():
    return {"message": "Fast API in Python"}


@app.get("/user")
def read_user():
    return api.read_user()


@app.get("/question/{position}", status_code=200)
def read_questions(position: int, response: Response):
    question = api.read_questions(position)

    if not question:
        raise HTTPException(status_code=400, detail="Error")

    return question


@app.get("/alternatives/{question_id}")
def read_alternatives(question_id: int):
    return api.read_alternatives(question_id)


@app.post("/answer", status_code=201)
def create_answer(payload: UserAnswer):
    payload = payload.dict()

    return api.create_answer(payload)


@app.get("/result/{user_id}")
def read_result(user_id: int):
    return api.read_result(user_id)


def start_fastapi(msg):
    logger.info(f'udp server port: 8990')
    logger.info('start up udp service')

    # reactor.callLater(1.5, start_udp, "hello, world")
    reactor.listenUDP(8990, EchoUDP())
    reactor.run()
    print("reactor exit")


if __name__ == "__main__":
    try:
        p = Process(target=start_fastapi, args=('main',))
        p.start()
        # p.join()
        logger.info(f'start start_fastapi:')
        logger.info(f'current cwd: {os.getcwd()}')
        uvicorn.run(app, port=8089, reload=False)
        logger.info('uvicorn exist')

    except Exception as ex:
        logger.error(ex)
        input('press any to exit key')
