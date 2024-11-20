from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from qfluentwidgets import (SwitchButton,GroupHeaderCardWidget)
from qfluentwidgets import (IconWidget,CaptionLabel, BodyLabel, toggleTheme, Pivot, qrouter,SegmentedWidget)
from ..common.style_sheet import StyleSheet


class PivotInterface(QWidget):
    """ Pivot interface """

    Nav = Pivot

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(800, 120)
        self.wifiWidget = QWidget()
        self.bleWidget = QWidget()
        self.wireWidget = QWidget()
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.wifiSwitchButton = SwitchButton('Off')
        self.bleSwitchButton = SwitchButton('Off')
        self.wireSwitchButton = SwitchButton('Off')

        self.wifiInterface(self.wifiWidget)
        self.bleInterface(self.bleWidget)
        self.wireInterface(self.wireWidget)

        # add items to pivot
        self.addSubInterface(self.wifiWidget, 'wifiWidget', 'WIFI连接')
        self.addSubInterface(self.bleWidget, 'bleWidget', '蓝牙连接')
        self.addSubInterface(self.wireWidget, 'wireWidget', '有线连接')

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.wifiWidget)
        self.pivot.setCurrentItem(self.wifiWidget.objectName())

        qrouter.setDefaultRouteKey(self.stackedWidget, self.wifiWidget.objectName())

    def wifiInterface(self, widget: QWidget):
        hBoxLayout = QHBoxLayout(widget)
        iconWidget = IconWidget(':/gallery/images/wifi.png')
        titleLabel = BodyLabel('EK3通过wifi更新网络数据')
        contentLabel = CaptionLabel('请注意EK3暂不支持连接WIFI6以及WPA认证的网络')
        textLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        iconWidget.setFixedSize(20, 20)
        contentLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        textLayout.addWidget(titleLabel)
        textLayout.addWidget(contentLabel)
        hBoxLayout.addWidget(iconWidget)
        hBoxLayout.addLayout(textLayout)
        hBoxLayout.addStretch(1)

        hBoxLayout.setSpacing(15)
        hBoxLayout.setContentsMargins(24, 10, 24, 10)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        textLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subLayout.addWidget(self.wifiSwitchButton)
        hBoxLayout.addLayout(subLayout)

        return hBoxLayout

    def bleInterface(self, widget: QWidget):
        hBoxLayout = QHBoxLayout(widget)
        iconWidget = IconWidget(':/gallery/images/ble.png')
        titleLabel = BodyLabel('EK3通过蓝牙更新网络数据')
        contentLabel = CaptionLabel('请保持本程序在后台常驻，以维持与EK3的通信')
        textLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        iconWidget.setFixedSize(20, 20)
        contentLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        textLayout.addWidget(titleLabel)
        textLayout.addWidget(contentLabel)
        hBoxLayout.addWidget(iconWidget)
        hBoxLayout.addLayout(textLayout)
        hBoxLayout.addStretch(1)

        hBoxLayout.setSpacing(15)
        hBoxLayout.setContentsMargins(24, 10, 24, 10)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        textLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subLayout.addWidget(self.bleSwitchButton)
        hBoxLayout.addLayout(subLayout)

        return hBoxLayout
    
    def wireInterface(self, widget: QWidget):
        hBoxLayout = QHBoxLayout(widget)
        iconWidget = IconWidget(':/gallery/images/connect2.png')
        titleLabel = BodyLabel('EK3通过有线方式更新网络数据')
        contentLabel = CaptionLabel('请保持本程序在后台常驻以及type-c连接')
        textLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        iconWidget.setFixedSize(20, 20)
        contentLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        textLayout.addWidget(titleLabel)
        textLayout.addWidget(contentLabel)
        hBoxLayout.addWidget(iconWidget)
        hBoxLayout.addLayout(textLayout)
        hBoxLayout.addStretch(1)

        hBoxLayout.setSpacing(15)
        hBoxLayout.setContentsMargins(24, 10, 24, 10)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        textLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subLayout.addWidget(self.wireSwitchButton)
        hBoxLayout.addLayout(subLayout)

        return hBoxLayout

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

class SegmentedInterface(PivotInterface):

    Nav = SegmentedWidget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout.removeWidget(self.pivot)
        self.vBoxLayout.insertWidget(0, self.pivot)

class ConnectCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("数据更新方式设置（时间，天气等）")
        self.setBorderRadius(15)

        self.nav = SegmentedInterface()
        self.groupLayout.addWidget(self.nav, alignment=Qt.AlignLeft)
        self.groupWidgets.append(self.nav)
