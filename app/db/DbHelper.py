import os

import pandas
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from distutils.log import error
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import  sessionmaker
from app.common.logger import logger
import logging
from sqlalchemy.exc import SQLAlchemyError
 


sqlaurl =os.environ.get('sqlalchemy_url', "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')) 
logger.info(
    f'dbhelper engine url: ' + os.environ.get('sqlalchemy_url', "sqlite:///" + os.path.join(os.getcwd(), 'fast.db')))
engine = create_engine(sqlaurl)
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
def ExecuteQuery(sql):
    try:
        with engine.connect() as con:
            data = con.execute(sql)
            return pandas.DataFrame(data)
            # inner context calls session.commit(), if there were no exceptions
            # outer context calls session.close()
    except Exception as ex:
        logger.error(ex)
        raise ex
class connectToDB():
    
    def __init__(self):
        try:
            self.engine = sqlalchemy.create_engine(sqlaurl)
            self.engine_session = sessionmaker(self.engine)
            sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
            # sqlalchemy_log.setLevel(logging.DEBUG)
            sqlalchemy_log.addHandler(InterceptHandler())
            
        except Exception as e:
              logger.error(f"{str(e)}  db init  ")
       
    def Select_sqlalchemy(self,sql):
        """ sqlalchemy
         如果空集，也會帶列名
        Args:
            sql (_type_): _description_

        Returns:
            _type_: _description_
        """        
        try:
            with self.engine.connect() as connection:
                result = pd.read_sql(sql, connection)# 會有字符問題
                # result.columns=map(lambda x: x if type(x)!= str else x.upper() , result.columns)s
                return result
        except SQLAlchemyError as exc:
            logger.error(str(exc))
            error, = exc.orig.args # 
            logger.error(f"Oracle-Error-Code:{ error.code}")
            logger.error(f"Oracle-Error-Message:{error.message}")
            raise exc #返回自定義錯誤類型
        except Exception  as e:
            logger.error(f"{str(e)} ")
            raise e
     
    def Select_scalar_sqlalchemy(self,sql):
        """sqlalchemy
         获取第一行的第一列，并关闭结果集。
        如果没有要获取的行，则返回None。
        不执行验证来测试是否还有其他行。
        调用此方法后，对象将完全关闭，

        Args:
            sql (_type_): _description_

        Raises:
            wx: _description_
            wx: _description_

        Returns:
            _type_: _description_
        """          
        try:
            with self.engine.connect() as connection:
                result =  connection.execute(sql)
                return result.scalar()
        except SQLAlchemyError as exc:
            logger.error(str(exc))
            error, = exc.orig.args # 
            logger.error(f"Oracle-Error-Code:{ error.code}")
            logger.error(f"Oracle-Error-Message:{error.message}")
            raise exc #返回自定義錯誤類型
        except Exception  as e:
            logger.error(f"{str(e)} ")
            raise e
                    
    def Select_scalars(self,sql:str,index = 0):
        """sqlalchemy
      返回A ScalarResult 将返回单个元素而不是 Row 物体
      index¶ -- 整数或行键，指示要从每行提取的列，默认为 0 表示第一列。
        Args:
            sql (_type_): _description_
            index (int, optional): _description_. Defaults to 0.

        Raises:
            wx: _description_
            wx: _description_

        Returns:
            _type_: _description_
        """         
        try:
            with self.engine.connect() as connection:
                result =  connection.execute(sql)
                return result.scalars(index).all()
        except SQLAlchemyError as exc:
            logger.error(str(exc))
            error, = exc.orig.args # 
            logger.error(f"Oracle-Error-Code:{ error.code}")
            logger.error(f"Oracle-Error-Message:{error.message}")
            raise exc #返回自定義錯誤類型
        except Exception  as e:
            logger.error(f"{str(e)} ")
           
            raise e
                    
                     
    def SqlExecute4(self,sql):
        '''
         執行一條,return  影响的行数
        '''
        try:
           
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.rowcount #  This read-only attribute specifies the number of rows that have currently been fetched from the cursor (for select statements), that have been affected by the operation (for insert, update, delete and merge statements), or the number of successful executions of the statement (for PL/SQL statements).
        
        except Exception  as e:
            logger.error(f"{str(e)}  SQL: {sql}")
            raise e

    def allSqlExecute4(self,sql_list):
        '''
         執行多條,return  影响的行数array
        '''
        try:
            rowcount = []
            for sql in sql_list:
                 self.cursor.execute(sql)
                 rowcount.append(self.cursor.rowcount)
            
            self.conn.commit()
            # self.cursor.executemany(sql_list,arraydmlrowcounts=True)
            # self.conn.commit()
            return rowcount # self.cursor.getarraydmlrowcounts()   
            # Cursor.getarraydmlrowcounts()
            # Retrieve the DML row counts after a call to executemany() with arraydmlrowcounts enabled. This will return a list of integers corresponding to the number of rows affected by the DML statement for each element of the array passed to executemany().
        except Exception as e:
            self.conn.rollback() # 回滾
            logger.error(f"{str(e)}")
            print(f'{self.config["DBname"]}:sql执行报错!')
   

    def sqlExcuteNoQueryBatch(self,sql_list):
        """ 執行多條
        出錯會自動rollback
        Args:
            sql_list (list): sql arrays
        
        Returns:
            _type_: 影响的行数 數組
        """        

        try:
            if not isinstance(sql_list,list):
                raise Exception('非數組sql!')
            result = []
            with self.engine.connect() as conn,conn.begin():
                for item in sql_list:
                    ele = conn.execute(item)
                    result.append(ele.rowcount)
            return  result
        

        except SQLAlchemyError as exc:
            logger.error(str(exc))
            error, = exc.orig.args # 
            logger.error(f"Oracle-Error-Code:{ error.code}")
            logger.error(f"Oracle-Error-Message:{error.message}")
            raise exc #返回自定義錯誤類型
        except Exception  as e:
            logger.error(f"{str(e)} ")
            raise e


   
 
class InterceptHandler(logging.Handler):
    def emit(self,record):
        logger_opt = logger.opt(depth = 6 , exception = record.exc_info)
        logger_opt.log(record.levelno,record.getMessage())


