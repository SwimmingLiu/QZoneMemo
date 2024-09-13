import sys
import os
# 兼容ui路径
UI_PATH = ["ui", "ui/login"]
sys.path.extend([os.path.join(os.getcwd(), path) for path in UI_PATH])
import logging
# 禁止标准输出
# sys.stdout = open(os.devnull, 'w')
logging.disable(logging.CRITICAL)  # 禁用所有级别的日志
from PySide6.QtGui import QIcon, Qt, QPalette
from PySide6.QtWidgets import QApplication, QLabel
from utils import glo
from qzonememo.QZoneMemoWindow import QZoneMemoWindow
from qzonememo.LoginWindow import LoginWindow

if __name__ == '__main__':
    app = QApplication([])  # 创建应用程序实例
    app.setWindowIcon(QIcon('images/Logo.ico'))  # 设置应用程序图标

    # 为整个应用程序设置样式表，去除所有QFrame的边框
    app.setStyleSheet("QFrame { border: none; }")

    # 创建窗口实例
    login_window = LoginWindow()
    qzonememo_window = QZoneMemoWindow()

    # 检查系统是否为夜间模式
    palette = app.palette()
    is_dark_mode = palette.color(QPalette.Window).value() < 128  # 判断是否是夜间模式

    # if is_dark_mode:
    #     # 如果是夜间模式，修改login_window和qzonememo_window的字体颜色为黑色
    #     app.setStyleSheet("QLabel{color: black; background-color:white;}")

    # 初始化全局变量管理器，并设置值
    glo._init()  # 初始化全局变量空间
    glo.set_value('login_window', login_window)  # 存储login_window窗口实例
    glo.set_value('qzonememo_window', qzonememo_window)  # 存储rqzonememo_window窗口实例
    # 从全局变量管理器中获取窗口实例
    login_window_glo = glo.get_value('login_window')

    # 显示LoginWindow窗口
    login_window_glo.show()
    app.exec()  # 启动应用程序的事件循环
