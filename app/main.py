import imp
import os

# from fastapi_sqlalchemy import DBSessionMiddleware
os.environ['sqlalchemy_url'] = "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')
import time
from multiprocessing import Process
import multiprocessing as mp
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
import psutil as ps

app = FastAPI()
fastapi_sqla.setup(app)
sched = TwistedScheduler()
sched.start()

api.start_Schedule()


class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        self.transport.write(datagram, address)
        print(datagram)
        print("sleep3")
        sched.add_job(func=api.event_record_json, args=(datagram, address))
        # msg, sock = datagram
        resp = time.ctime()
        self.transport.write(resp.encode('ascii'), address)


@app.get("/api/events")
def get_events():
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


def start_udp(port):
    logger.info(f'current udp process pid : {os.getpid()}')
    logger.info(f'udp server port:  {port}')
    logger.info('start up udp service')
    # reactor.callLater(1.5, start_udp, "hello, world")
    reactor.listenUDP(port, EchoUDP())
    reactor.run()
    print("reactor exit")


if __name__ == "__main__":
    try:
        logger.info(f'current program pid : {os.getpid()}')
        mp.freeze_support()  # 为使用了 multiprocessing  的程序，提供冻结以产生 Windows 可执行文件的支持。
        p = Process(target=start_udp, args=(11000,))
        p.start()
        # p.join()
        logger.info(f'start start_fastapi:')
        logger.info(f'current cwd: {os.getcwd()}')
        uvicorn.run(app, port=21000, reload=False)
        logger.info('uvicorn exist')

    except Exception as ex:
        logger.error(ex)
        input('press any to exit key')
