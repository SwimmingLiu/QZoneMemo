# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LoginUI.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QMainWindow,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets import (PixmapLabel, SubtitleLabel, TitleLabel)
import LoginUI_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(487, 512)
        MainWindow.setStyleSheet(u"QMainWindow#MainWindow{\n"
"background: qlineargradient(\n"
"    spread:pad,\n"
"    x1:0, y1:0,\n"
"    x2:0, y2:1,\n"
"    stop:0 #f3ffff,\n"
"    stop:0.5 #f9ffe3,\n"
"    stop:1 #ffedf3\n"
");\n"
"\n"
"	border-radius: 15%;\n"
"}")
        MainWindow.setIconSize(QSize(60, 60))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.title = QFrame(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setStyleSheet(u"QFrame#title{\n"
"	border: 0px solid rgba(0, 0, 0, 0.073);\n"
"	border-bottom: 1px solid rgba(0, 0, 0, 0.183);\n"
"}	\n"
"")
        self.title.setFrameShape(QFrame.StyledPanel)
        self.title.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.title)
        self.horizontalLayout_2.setSpacing(1)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.PixmapLabel = PixmapLabel(self.title)
        self.PixmapLabel.setObjectName(u"PixmapLabel")
        self.PixmapLabel.setStyleSheet(u"image:url(:/login/images/QzoneLogo.png);")

        self.horizontalLayout_2.addWidget(self.PixmapLabel)

        self.frame = QFrame(self.title)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.TitleLabel_2 = TitleLabel(self.frame)
        self.TitleLabel_2.setObjectName(u"TitleLabel_2")
        self.TitleLabel_2.setStyleSheet(u"font: 20pt \"Times New Roman\";")

        self.horizontalLayout.addWidget(self.TitleLabel_2)

        self.TitleLabel = TitleLabel(self.frame)
        self.TitleLabel.setObjectName(u"TitleLabel")
        self.TitleLabel.setStyleSheet(u"font: 20pt \"\u9ed1\u4f53\";")

        self.horizontalLayout.addWidget(self.TitleLabel)


        self.horizontalLayout_2.addWidget(self.frame)

        self.horizontalLayout_2.setStretch(0, 5)
        self.horizontalLayout_2.setStretch(1, 10)

        self.verticalLayout.addWidget(self.title)

        self.mainbox = QFrame(self.centralwidget)
        self.mainbox.setObjectName(u"mainbox")
        self.mainbox.setStyleSheet(u"")
        self.mainbox.setFrameShape(QFrame.StyledPanel)
        self.mainbox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.mainbox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.qrcode_img = PixmapLabel(self.mainbox)
        self.qrcode_img.setObjectName(u"qrcode_img")
        self.qrcode_img.setStyleSheet(u"image:url(:/qrcode/images/QRcodeLogo.png)")
        self.qrcode_img.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.qrcode_img)

        self.message_bar = SubtitleLabel(self.mainbox)
        self.message_bar.setObjectName(u"message_bar")
        self.message_bar.setStyleSheet(u"font: 700 15pt \"\u5b8b\u4f53\";\n"
"")
        self.message_bar.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.message_bar)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 100)
        self.verticalLayout_2.setStretch(2, 10)

        self.verticalLayout.addWidget(self.mainbox)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 8)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"QZoneMemo", None))
        self.TitleLabel_2.setText(QCoreApplication.translate("MainWindow", u"QZoneMemo - ", None))
        self.TitleLabel.setText(QCoreApplication.translate("MainWindow", u"\u7a7a\u95f4\u56de\u5fc6\u5f55", None))
        self.message_bar.setText(QCoreApplication.translate("MainWindow", u"\u83b7 \u53d6 \u767b \u5f55 \u9a8c \u8bc1 \u7801 . . .", None))
    # retranslateUi

