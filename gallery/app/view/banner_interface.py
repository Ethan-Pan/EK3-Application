from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import (FluentIcon, FluentIcon,isDarkTheme)
from ..common.config import HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..components.link_card import LinkCardView


class EKBannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Define your EK', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('EKgalleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/userManual.png',
            self.tr('User Manual'),
            self.tr('用户操作指导手册，设备操作与设置相关信息可以访问查询'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub REPO'),
            self.tr(
                'EK3 github仓库，包括EK3固件源码以及EK Home程度源码'),
            REPO_URL
        )

        self.linkCardView.addCard(
            ':/gallery/images/hardware.png',
            self.tr('Hardware'),
            self.tr(
                'EK3硬件设计资料，包含结构文件，原理图，PCB以及器件BOOM'),
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            ':/gallery/images/feedback.png',
            self.tr('Send feedback'),
            self.tr('欢迎大家反馈bug，一起推动EK3成为真正好用的产品'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))