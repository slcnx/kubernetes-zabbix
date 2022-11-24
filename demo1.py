import logging
import random
import sys
import time
import signal
import coloredlogs

# logging.DEBUG
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
from config import Configuration
from daemon_thread import CheckDaemon
if __name__ == '__main__':

    config = Configuration()

    # 从配置文件加载配置
    config.load_config_ini()


    formatter_string: str = config.formatter_string
    formatter = logging.Formatter(formatter_string)

    # 定义root handler
    coloredlogs.install(fmt=formatter_string)  # 默认INFO

    # 定义logger
    logger = logging.getLogger(__file__)

    daemons: list[CheckDaemon] = []

    daemons.append(CheckDaemon(config=config,resources=['pods']))

    # Daemon start
    try:
        logger.info("Starting daemon threads now")
        for daemon in daemons:
            daemon.run()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("got SIGINT, shutting down")
        for daemon in daemons:
            daemon.handler(signal.SIGTERM)
        sys.exit(1)