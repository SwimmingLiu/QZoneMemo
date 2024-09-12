import datetime
import logging
from colorlog import ColoredFormatter

class LoggerUtils:
    def __init__(self, taskname = None):

        if taskname is None:
            taskname = 'default'

        # 创建一个日志器
        self.logger = logging.getLogger(f'example_logger_{taskname}')
        self.logger.setLevel(logging.INFO)

        # 获取当前日期和时间
        current_time = datetime.datetime.now()
        # 格式化时间字符串，例如：2024-05-11_15-30-00
        formatted_time = current_time.strftime('%Y-%m-%d_%H-%M-%S')
        # 创建文件名
        if taskname:
            log_name_path = f'logs/{taskname}_counting_{formatted_time}.txt'
        else:
            log_name_path = f'logs/{taskname}_counting_{formatted_time}.txt'

        # 检查日志器是否已经有处理器，避免重复添加
        if not self.logger.hasHandlers():
            # 创建彩色日志格式，包括时间戳
            log_format = "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(blue)s%(message)s"
            formatter = ColoredFormatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

            # 创建一个流处理器，并将其添加到日志器
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            # 添加文件流处理器
            file_handler = logging.FileHandler(log_name_path)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                               datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def info(self, msg):
        self.logger.info(str(msg))


if __name__ == "__main__":
    loggertool = LoggerUtils()
    loggertool.logger.info("test")

