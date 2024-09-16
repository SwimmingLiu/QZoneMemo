import os
import shutil
import time
import webbrowser
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import platform
import subprocess
from qzonememo.GUIWindow import GUIWindow
from qzonethread.FindQZoneMemoThread import FindQZoneMemoThread
from ui.qzone_memo import Ui_MainWindow
from utils import glo
from PySide6.QtCore import QPropertyAnimation


class QZoneMemoWindow(GUIWindow):
    def __init__(self):
        super().__init__()
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

        # --- 找回QQ空间历史记录 --- #
        self.find_qzone_memo_thread = FindQZoneMemoThread()
        self.ui.find_memo.clicked.connect(self.findMemo)
        self.ui.export_excel.clicked.connect(self.exportExcel)
        self.ui.show_memo.clicked.connect(self.showMemo)
        # --- 找回QQ空间历史记录 --- #

        # --- 进度条 --- #
        self.find_qzone_memo_thread.send_login_status.connect(lambda msg: self.createSuccessInfoBar("登录状态", msg))
        self.find_qzone_memo_thread.send_progress.connect(lambda x: self.ui.progress_bar.setValue(int(x)))
        self.find_qzone_memo_thread.send_message.connect(lambda msg: self.showStatus(msg))
        self.find_qzone_memo_thread.send_result.connect(lambda msg: self.createSuccessInfoBar("提示", msg))
        # --- 进度条 --- #

    # 展示网页版回忆录
    def showMemo(self):
        # 使用默认浏览器打开
        if self.find_qzone_memo_thread.render_html_url:
            webbrowser.open(self.find_qzone_memo_thread.render_html_url)
        else:
            self.createErrorInfoBar("提示", "尚未完成找回QQ空间回忆任务！")

    # 打开Excel窗口
    def exportExcel(self):
        # 获取当前系统平台
        path = os.path.join(self.current_workpath, self.config.result_path)
        if not os.path.exists(path) or len(os.listdir(path)) == 0:
            self.createErrorInfoBar("提示", "尚未完成找回QQ空间回忆任务，或您尚未发表过说说！")
            return
        current_platform = platform.system()
        if current_platform == "Windows":
            # Windows 使用 os.startfile
            os.startfile(path)
        elif current_platform == "Darwin":
            # macOS 使用 'open'
            subprocess.Popen(["open", path])
        elif current_platform == "Linux":
            # Linux 使用 'xdg-open'
            subprocess.Popen(["xdg-open", path])
        else:
            print(f"不支持的操作系统: {current_platform}")

    # 找回回忆
    def findMemo(self):
        self.showStatus('开 始 找 回 Q Q 空 间 回 忆 ...')
        if self.find_qzone_memo_thread.isRunning():
            self.find_qzone_memo_thread.quit()
        self.find_qzone_memo_thread.start()
        # self.fixfont_thread.set_path(self.excel_input_path, self.excel_result_path)
        # self.fixfont_thread.send_result.connect(lambda x: self.resultInfo(x))
        # self.fixfont_thread.start()

    # 显示通知消息
    def showStatus(self, msg):
        self.ui.message_box.setText(msg)

    def showEvent(self, event):
        super().showEvent(event)
        if not event.spontaneous():
            # 这里定义显示动画
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(800)  # 动画时间500毫秒
            self.animation.setStartValue(0)  # 从完全透明开始
            self.animation.setEndValue(1)  # 到完全不透明结束
            self.animation.start()

    # --- 关闭窗口 自动删除Result缓存 --- #
    def closeEvent(self, event):
        if not self.animation_window:
            self.animation_window = QPropertyAnimation(self, b"windowOpacity")
            self.animation_window.setStartValue(1)
            self.animation_window.setEndValue(0)
            self.animation_window.setDuration(500)
            self.animation_window.start()
            self.animation_window.finished.connect(self.close)
            try:
                if os.path.exists(self.config.temp_path):
                    shutil.rmtree(self.config.temp_path)
                if os.path.exists(self.config.user_path):
                    shutil.rmtree(self.config.user_path)
                if os.path.exists(self.config.fetch_all_path):
                    shutil.rmtree(self.config.fetch_all_path)
            except Exception:
                time.sleep(1)
                if os.path.exists(self.config.temp_path):
                    shutil.rmtree(self.config.temp_path)
                if os.path.exists(self.config.user_path):
                    shutil.rmtree(self.config.user_path)
                if os.path.exists(self.config.fetch_all_path):
                    shutil.rmtree(self.config.fetch_all_path)
            event.ignore()
    # --- 关闭窗口 自动删除Result缓存 --- #


# 测试
if __name__ == '__main__':
    app = QApplication([])  # 创建应用程序实例
    app.setWindowIcon(QIcon('images/logo.ico'))  # 设置应用程序图标

    # 为整个应用程序设置样式表，去除所有QFrame的边框
    app.setStyleSheet("QFrame { border: none; }")

    # 创建窗口实例
    qzonememo_window = QZoneMemoWindow()

    # 初始化全局变量管理器，并设置值
    glo._init()  # 初始化全局变量空间
    glo.set_value('qzonememo_window', qzonememo_window)  # 存储randy_window窗口实例

    # 从全局变量管理器中获取窗口实例
    qzonememo_window_glo = glo.get_value('qzonememo_window')

    # 显示yoloshow窗口
    qzonememo_window_glo.show()
    app.exec()  # 启动应用程序的事件循环
