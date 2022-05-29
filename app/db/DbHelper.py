import os
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger.info(
    f'dbhelper engine url ' + os.environ.get('sqlalchemy_url', "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')))
engine = create_engine(os.environ.get('sqlalchemy_url', "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')))
Session = sessionmaker(bind=engine)


def ExecuteAdd(obj):
    try:
        with Session() as session, session.begin():
            session.add(obj)
            # inner context calls session.commit(), if there were no exceptions
            # outer context calls session.close()
    except Exception as ex:
        logger.error(ex)
        raise ex
