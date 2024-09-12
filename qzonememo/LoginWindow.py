import json
import os
import shutil
import time

import cv2
from PySide6.QtGui import QIcon, QImage, QPixmap, QPainter
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PySide6.QtGui import QMouseEvent, QGuiApplication
from qfluentwidgets import InfoBar, InfoBarPosition

from qzonememo.GUIWindow import GUIWindow
from qzonethread.LoginThread import QQLoginThread
from ui.external.customGrips import CustomGrip
from ui.login.LoginUI import Ui_MainWindow
from utils import glo
from PySide6.QtCore import Qt, QPropertyAnimation


class LoginWindow(GUIWindow):
    def __init__(self):
        super().__init__()
        self.current_workpath = os.getcwd()
        self.animation_window = None

        # --- 拖动窗口 改变窗口大小 --- #
        self.center()  # 窗口居中
        self.setAcceptDrops(False)  # ==> 设置窗口支持拖动（必须设置）
        # --- 拖动窗口 改变窗口大小 --- #

        # --- 加载UI --- #
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 固定窗口大小，禁止缩放
        self.setFixedSize(self.width(), self.height())
        # --- 加载UI --- #

        # --- LoginThread --- #
        self.login_thread = QQLoginThread()
        self.login_thread.send_qrcode.connect(lambda img: self.showImage(img))
        self.login_thread.send_qrcode_result.connect(lambda msg: self.showQRcodeResult(msg))
        self.login_thread.send_cookies.connect(self.transfer2QZoneMemoWindow)
        self.login_thread.start()
        # --- LoginThread --- #

    def transfer2QZoneMemoWindow(self):
        qzonememo_window_glo = glo.get_value("qzonememo_window")
        self.close()
        qzonememo_window_glo.show()


    def showQRcodeResult(self, msg):
        if '二维码认证中' in msg:
            self.createSuccessInfoBar('登录提示', '扫描二维码成功')
        elif '二维码已失效' in msg:
            self.createErrorInfoBar('登录提示', '二维码已失效, 重新获取登录二维码', duration=1000)
            # 重新获取验证吗
            if self.login_thread.isRunning():
                self.login_thread.quit()
            self.login_thread.start()
        elif '取消登录' in msg:
            self.createErrorInfoBar('登录提示', '您已取消登陆, 登陆需重扫二维码')
        elif '登录成功' in msg:
            self.createSuccessInfoBar('登录提示', '登录成功!')

    # 展示二维码
    def showImage(self, img):
        try:
            img_src = img
            ih, iw = img_src.shape
            w = self.ui.qrcode_img.geometry().width()
            h = self.ui.qrcode_img.geometry().height()

            # 保持原始宽高比
            if iw / w > ih / h:
                scal = w / iw
                nw = w
                nh = int(scal * ih)
                img_src_ = cv2.resize(img_src, (nw, nh))
            else:
                scal = h / ih
                nw = int(scal * iw)
                nh = h
                img_src_ = cv2.resize(img_src, (nw, nh))

            frame = cv2.cvtColor(img_src_, cv2.COLOR_BGR2RGB)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * frame.shape[2],
                         QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(img)

            # 创建空白pixmap用于居中
            full_pixmap = QPixmap(w, h)
            full_pixmap.fill(Qt.transparent)  # 填充透明色

            # 计算偏移量以使图像居中
            x_offset = (w - nw) // 2
            y_offset = (h - nh) // 2

            # 在居中的位置绘制图像
            painter = QPainter(full_pixmap)
            painter.drawPixmap(x_offset, y_offset, pixmap)
            painter.end()

            # 设置PixMap
            self.ui.qrcode_img.setPixmap(full_pixmap)
            self.createSuccessInfoBar("登录提示", "登录二维码获取成功!", duration=1000)
            self.ui.message_bar.setText("扫 码 登 录 Q Q 空 间")
        except Exception as err:
            print(f"Show QRcode Err:{err}")




# 测试
if __name__ == '__main__':
    app = QApplication([])  # 创建应用程序实例
    app.setWindowIcon(QIcon('images/Logo.ico'))  # 设置应用程序图标

    # 为整个应用程序设置样式表，去除所有QFrame的边框
    app.setStyleSheet("QFrame { border: none; }")

    # 创建窗口实例
    login_window = LoginWindow()

    # 初始化全局变量管理器，并设置值
    glo._init()  # 初始化全局变量空间
    glo.set_value('login_window', login_window)  # 存储randy_window窗口实例

    # 从全局变量管理器中获取窗口实例
    login_window_glo = glo.get_value('login_window')

    # 显示yoloshow窗口
    login_window_glo.show()
    app.exec()  # 启动应用程序的事件循环
