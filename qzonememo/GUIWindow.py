import os

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QMouseEvent, QGuiApplication
from qfluentwidgets import InfoBar, InfoBarPosition

from utils.ConfigUtil import ConfigUtil
from PySide6.QtCore import Qt, QPropertyAnimation


class GUIWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.current_workpath = os.getcwd()
        self.animation_window = None
        self.config = ConfigUtil()

    # --- 拖动窗口 改变窗口大小 窗口居中 --- #
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_start_pt = event.globalPosition().toPoint()
            self.window_pos = self.frameGeometry().topLeft()
            self.drag = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag:
            distance = event.globalPosition().toPoint() - self.mouse_start_pt
            self.move(self.window_pos + distance)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.drag = False

    def center(self):
        # PyQt6获取屏幕参数
        screen = QGuiApplication.primaryScreen().size()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2 - 10)


    # --- 拖动窗口 改变窗口大小 窗口居中 --- #

    # --- InfoBar --- #
    def createErrorInfoBar(self, title, content, duration=2000):
        return InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,  # won't disappear automatically
            parent=self
        )

    def createSuccessInfoBar(self, text, content, duration=2000):
        # convenient class mothod
        return InfoBar.success(
            title=text,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=duration,
            parent=self
        )

    # --- InfoBar --- #

    # --- 关闭窗口 自动删除Result缓存 --- #
    def closeEvent(self, event):
        if not self.animation_window:
            self.animation_window = QPropertyAnimation(self, b"windowOpacity")
            self.animation_window.setStartValue(1)
            self.animation_window.setEndValue(0)
            self.animation_window.setDuration(500)
            self.animation_window.start()
            self.animation_window.finished.connect(self.close)
    # --- 关闭窗口 自动删除Result缓存 --- #

# 测试
