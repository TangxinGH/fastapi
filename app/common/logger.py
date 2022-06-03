import os
import time
from loguru import logger

basedir = os.path.dirname(os.path.abspath(__package__))

# 定位到log日志文件
# log_path = os.path.join(basedir, 'logs')
log_path = os.path.join(basedir,  'logs')#多個逗號,以區分windows and linux
if not os.path.exists(log_path):
    # os.mkdir(log_path)
    os.makedirs(log_path)#递归的方式创建文件夹

log_path_all = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_log.log')
log_path_info = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_info.log')
log_path_debug = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_debug.log')
log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_error.log')
log_path_sql = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_sql.log')
log_path_trace = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_sql.log')

new_level = logger.level("SQL", no=38, color="<yellow>", icon="🐍")# logger.log("SNAKY", "Here we go!")
# 日志简单配置
# 具体其他配置 可自行参考 https://github.com/Delgan/loguru
logger.add(log_path_all, rotation="200 MB", enqueue=True,encoding  = "UTF-8")
logger.add(log_path_info, rotation="00:00", retention="15 days",enqueue=True,level='INFO',encoding  = "UTF-8")
logger.add(log_path_debug, rotation="00:00", retention="15 days", enqueue=True,level='DEBUG',encoding  = "UTF-8") # 日志等级分割
logger.add(log_path_error, rotation="00:00", retention="15 days", enqueue=True,level='ERROR',encoding  = "UTF-8") # 日志等级分割
logger.add(log_path_sql, rotation="100 MB", retention="3 days", enqueue=True,level='SQL',encoding  = "UTF-8") # 日志等级分割
logger.add(log_path_trace, rotation="100 MB", retention="3 days", enqueue=True,level='TRACE',encoding  = "UTF-8") # 日志等级分割


 