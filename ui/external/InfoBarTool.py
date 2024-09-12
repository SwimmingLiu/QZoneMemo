from qfluentwidgets import InfoBar, InfoBarPosition
from PySide6.QtCore import Qt, QTranslator, QLocale


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
