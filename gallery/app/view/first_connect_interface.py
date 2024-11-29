from PySide6.QtCore import Qt
from qfluentwidgets import (GroupHeaderCardWidget, TogglePushButton,InfoBar,InfoBarPosition)
from PySide6.QtCore import QTimer
from ..connect.uart import UartConnect
import os
import time

class FirstConnectCard(GroupHeaderCardWidget):
    def __init__(self, uart: UartConnect, parent=None):
        super().__init__(parent)
        self.uart_last_state = False
        self.setTitle("连接设备")
        self.setBorderRadius(15)
        self.uartConnect = uart
        self.button = TogglePushButton('连接')
        self.button.setFixedWidth(80)
        self.button.clicked.connect(self.button_clicked)
        self.first_connect_flag = os.path.exists(self.uartConnect.config_file)
        self.timer_check_connect = QTimer()
        self.timer_check_connect.timeout.connect(self.check_connect)
        if self.first_connect_flag:
            self.timer_check_connect.start(1000)

        self.addGroup(':/gallery/images/connect.png', "连接EK3", "请将EK3通过TypeC线接入EK Home，并点击右边连接按钮", self.button)

        self.stateTooltip = None

    def button_clicked(self):
        self.button.setText('连接中')
        InfoBar.warning(
            title='连接中',
            content="请不要断开设备与EK Home的连接",
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
        self.timer.start(1000)

    def delayed_action(self):
        # 停止计时器
        self.timer.stop()
        flag_connect = self.uartConnect.try_connect()
        print(f'-------flag_connect:{flag_connect}')
        if flag_connect:
            InfoBar.success(
            title='已连接',
            content="开始配置你的EK3吧！",
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2500,
            parent=self
            )
            self.button.setText('已连接')
            self.button.setEnabled(False)

            if self.first_connect_flag and not self.uartConnect.listen_open:
                self.uartConnect.run_uart_listen()
            
            if not self.first_connect_flag:
                self.timer_check_connect.start(1000)
            
        else:
            InfoBar.error(
                title='连接失败',
                content="请保持连接并已安装CH340驱动！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=3000,
            parent=self
            )
            self.button.setText('连接')
            self.button.setEnabled(True)
        
        
    def handle_connect_state(self, state):
        print(f'handle_connect_state:{state}')
        if state == True:
            self.connect_success()
        else:
            self.connect_failed()
            
    def connect_success(self):
        self.button.setText('已连接')
        self.button.setEnabled(False)
    
    def connect_failed(self):
        self.button.setText('连接')
        self.button.setEnabled(True)
        InfoBar.error(
            title='连接失败',
            content="请保持连接并已安装CH340驱动！",
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
            )
    
    def check_connect(self):
        flag_check = self.uartConnect.connected
        if not self.first_connect_flag:
            if not flag_check and self.uart_last_state:
                self.uart_last_state = False
                print('connect failed')
                self.connect_failed()
            if flag_check and not self.uart_last_state:
                self.uart_last_state = True
                print('connect success')
                self.connect_success()
        else:
            if not flag_check and self.uart_last_state:
                self.uart_last_state = False
                self.button.setText('连接中')
                self.button.setEnabled(False)
                print('connect failed222')
                InfoBar.error(
                    title='连接失败',
                    content="请保持连接并已安装CH340驱动！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                    )
            if flag_check and not self.uart_last_state:
                self.uart_last_state = True
                self.connect_success()

