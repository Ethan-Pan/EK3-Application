from PySide6.QtCore import Qt
from qfluentwidgets import (GroupHeaderCardWidget, TogglePushButton,InfoBar,InfoBarPosition)
from PySide6.QtCore import QTimer
from ..connect.uart import UartConnect

class FirstConnectCard(GroupHeaderCardWidget):
    def __init__(self, uart: UartConnect, parent=None):
        super().__init__(parent)
        self.setTitle("连接设备")
        self.setBorderRadius(15)

        self.uartConnect = uart

        self.button = TogglePushButton('连接')
        self.button.setFixedWidth(80)
        self.button.clicked.connect(self.button_clicked)

        self.addGroup(':/gallery/images/connect.png', "连接EK3", "请将EK3通过TypeC线接入PC，并点击右边按钮", self.button)

        self.stateTooltip = None

    def button_clicked(self):
        self.button.setText('连接中')
        InfoBar.warning(
            title='连接中',
            content="请不要断开设备与PC的连接。",
            orient=Qt.Horizontal,
            isClosable=False,   # disable close button
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self
        )
        
        # 创建一个QTimer对象
        self.timer = QTimer()
        self.timer.timeout.connect(self.delayed_action)
        # 设置延时时间为1000毫秒（1秒）
        self.timer.start(2000)

    def delayed_action(self):
        # 停止计时器
        self.timer.stop()
        flag_connect = self.uartConnect.try_connect()
        if flag_connect:
            InfoBar.success(
            title='已连接',
            content="开始配置你的EK3吧！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2500,
            parent=self
            )
            self.button.setText('已连接')
            self.button.setEnabled(False)

            self.timer2 = QTimer()
            self.timer2.timeout.connect(self.check_connect)
            # 设置延时时间为1000毫秒（1秒）
            self.timer2.start(1000)
        else:
            InfoBar.error(
            title='连接失败',
            content="请保持连接并已安装CH340驱动！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
            )
            self.button.setText('连接')
            self.button.setEnabled(True)
        

    
    def check_connect(self):
        flag_check = self.uartConnect.check_connection()
        if not flag_check:
            InfoBar.error(
            title='连接失败',
            content="请保持连接并已安装CH340驱动！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self
            )
            self.button.setText('连接')
            self.button.setEnabled(True)
            self.timer2.stop()