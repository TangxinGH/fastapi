import imp
import json
import os

# from fastapi_sqlalchemy import db
import socket

import requests
from fastapi_sqla import open_session
from app.model.dbmodels import Event, Schedule, SchedulesWeb
from app.common.logger import logger
from app.db.DbHelper import Session, ExecuteAdd, ExecuteQuery, connectToDB
import pandas as pd
from sqlalchemy.dialects import sqlite
import psutil as ps
from apscheduler.schedulers.background import BackgroundScheduler


def event_record():
    data = {}
    with Session() as session:
        sql = session.query(Event)  # all()
        raw = str(sql.statement.compile(dialect=sqlite.dialect()))
        data = ExecuteQuery(raw)

    return data


def event_record_json(*args, **kwargs):
    try:

        result = json.loads(args[0])
        logger.debug(result)
        ev = Event(**result)
        os.getcwd()

        ExecuteAdd(ev)

        # with open_session() as session:
        #     session.add(ev)
        #     session.commit()

        # with db():
        #     db.session.add(ev)
        #     db.session.commit()
    except Exception as ex:
        # logger.error(f'current cwd {os.getcwd()}')
        logger.error(ex)


def start_Schedule(*args, **kwargs):
    bgs = BackgroundScheduler()
    # bgs._daemon = False
    data = []
    with Session() as session:
        raw = str(session.query(Schedule).statement.compile(dialect=sqlite.dialect()))
        op = connectToDB()
        data = op.Select_sqlalchemy(raw)
    for k, item in data.iterrows():
        verbs = item.to_dict()
        bgs.add_job(exc_pid_check, item.How, name=item['SchName'] + '|' + item['What'],
                    minutes=float(item['Minutes']), args=[verbs])

    #     web scheduler
    with Session() as session:
        raw = str(session.query(SchedulesWeb).statement.compile(dialect=sqlite.dialect()))
        op = connectToDB()
        data = op.Select_sqlalchemy(raw)
    for k, item in data.iterrows():
        verbs = item.to_dict()
        bgs.add_job(exc_web_check, item.How, name=item.AppName + '|' + item.What,
                    minutes=float(item.Minutes), args=[verbs])

    bgs.start()  # 要調用start


def exc_pid_check(sch, *args, **kwargs):
    logger.info(sch['SchName'] + '|' + sch['What'])
    pids = ps.process_iter()
    ev = Event()
    ev.AppKey = sch['SchKey']
    ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Fail_Code']
    ev.EventCode = sch['SchKey'] + '|' + sch['Fail_Code']
    for pid in pids:
        if (pid.name() == sch['What']):
            logger.info(f"{sch['What']} pid is {pid}")
            ev.EventCode = sch['SchKey'] + '|' + sch['Success_Code']
            ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Success_Code']
            break
    ExecuteAdd(ev)


def exc_web_check(sch, *args, **kwargs):
    logger.info(sch['AppName'] + '|' + sch['What'])
    pids = ps.process_iter()
    ev = Event()
    ev.AppKey = sch['AppKey']
    ev.EventName = sch['AppName'] + '|' + sch['What'] + '|' + sch['Fail_Code']
    ev.EventCode = sch['AppKey'] + '|' + sch['Fail_Code']
    url = sch['What']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55"}
    try:
        response = requests.get(url, headers=headers, timeout=5).status_code
        logger.info(f'web checke res : {response}')
        if response == 200:
            logger.info(f"{sch['What']} web is  ok ")
            ev.EventCode = sch['AppKey'] + '|' + sch['Success_Code']
            ev.EventName = sch['AppName'] + '|' + sch['What'] + '|' + sch['Success_Code']
        else:
            logger.info(f"{sch['What']} web is  ng ")
            ev.EventName = sch['AppName'] + '|' + sch['What'] + '|' + sch['Fail_Code']
            ev.EventCode = sch['AppKey'] + '|' + sch['Fail_Code']
    except Exception as e:
        logger.error(f'web check error: {e}')

    ExecuteAdd(ev)


def exc_port_check(sch, *args, **kwargs):
    logger.info(sch['SchName'] + '|' + sch['What'])
    pids = ps.process_iter()
    ev = Event()
    ev.AppKey = sch['SchKey']
    ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Fail_Code']
    ev.EventCode = sch['SchKey'] + '|' + sch['Fail_Code']
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((sch.ip, sch.port))
            logger.info(f"{sch['What']} port is ok")
            ev.EventCode = sch['SchKey'] + '|' + sch['Success_Code']
            ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Success_Code']
    except  socket.error as e:
        logger.error(f'socket error check: {e}')

    ExecuteAdd(ev)

def exc_db_check(sch, *args, **kwargs):
    logger.info(sch['SchName'] + '|' + sch['What'])
    pids = ps.process_iter()
    ev = Event()
    ev.AppKey = sch['SchKey']
    ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Fail_Code']
    ev.EventCode = sch['SchKey'] + '|' + sch['Fail_Code']
    try:
            op = connectToDB()
            result = op.Select_scalars(sch['What'])
            if  eval(sch['Eval']):
                logger.info(f"{sch['What']} port is ok")
                ev.EventCode = sch['SchKey'] + '|' + sch['Success_Code']
                ev.EventName = sch['SchName'] + '|' + sch['What'] + '|' + sch['Success_Code']
    except  socket.error as e:
        logger.error(f'socket error check: {e}')

    ExecuteAdd(ev)



def read_user():
    with open('data/users.json') as stream:
        users = json.load(stream)

    return users


def read_questions(position: int):
    with open('data/questions.json') as stream:
        questions = json.load(stream)

    for question in questions:
        if question['position'] == position:
            return question


def read_alternatives(question_id: int):
    alternatives_question = []
    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for alternative in alternatives:
        if alternative['question_id'] == question_id:
            alternatives_question.append(alternative)

    return alternatives_question


def create_answer(payload):
    answers = []
    result = []

    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for question in payload['answers']:
        for alternative in alternatives:
            if alternative['question_id'] == question['question_id']:
                answers.append(alternative['alternative'])
                break

    with open('data/cars.json') as stream:
        cars = json.load(stream)

    for car in cars:
        if answers[0] in car.values() and answers[1] in car.values() and answers[2] in car.values():
            result.append(car)

    return result


def read_result(user_id: int):
    user_result = []

    with open('data/results.json') as stream:
        results = json.load(stream)

    with open('data/users.json') as stream:
        users = json.load(stream)

    with open('data/cars.json') as stream:
        cars = json.load(stream)

    for result in results:
        if result['user_id'] == user_id:
            for user in users:
                if user['id'] == result['user_id']:
                    user_result.append({'user': user})
                    break

        for car_id in result['cars']:
            for car in cars:
                if car_id == car['id']:
                    user_result.append(car)

    return user_result
