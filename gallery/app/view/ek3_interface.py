# coding:utf-8
import os
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (PrimaryPushButton,ScrollArea, PrimaryPushButton,TransparentToolButton,InfoBar,InfoBarPosition)
from qfluentwidgets import ScrollArea
from qfluentwidgets import FluentIcon as FIF
from functools import partial
from ..common.style_sheet import StyleSheet
from ..common.translator import Translator
from .user_interface import UserCard
from .connect_interface import ConnectCard
from .area_interface import AreaCard
from .first_connect_interface import FirstConnectCard
from .power_interface import PowerCard, PowerSaveCard
from .update_interface import UpdateCard
from .color_interface import ColorCard
from .banner_interface import EKBannerWidget
from .encorder_interface import EncoderCard
from .finger_interface import FingerCard, AddFingerCard
from .wifi_interface import WifiInterface
from ..connect.uart import UartConnect


class EKInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.uart = UartConnect()
        self.banner = EKBannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout1 = QVBoxLayout(self.view)
        self.vBoxLayout = QVBoxLayout()
        self.translator = Translator()
        self.userCard = UserCard(self)
        self.conectCard = ConnectCard(self)
        self.areaCard = AreaCard(self)
        self.firstConnectCard = FirstConnectCard(self.uart)
        self.powerCard = PowerCard()
        self.updateCard = UpdateCard()
        self.colorCard = ColorCard()
        self.powerSaveCard = PowerSaveCard()
        self.fingerCard = FingerCard()
        self.encoderCard = EncoderCard()
        self.addFingerCard = AddFingerCard(self.uart)
        self.wifiCard = WifiInterface()
        self.upDataButton = PrimaryPushButton(FIF.UPDATE, '一键同步配置')
        self.upDataButton.clicked.connect(self.on_update_clicked)

        self.conectCard.nav.wifiSwitchButton.checkedChanged.connect(self.showWifiInput)
        self.conectCard.nav.bleSwitchButton.checkedChanged.connect(self.bleSwitchState)
        self.conectCard.nav.wireSwitchButton.checkedChanged.connect(self.wireSwitchState)

        self.config_connect_flag = '0'
        self.config_info = {}

        self.__initWidget()
        self.ek_connect()
        self.initConfigInfo()

    def __initWidget(self):
        self.view.setObjectName('EKview')
        self.setObjectName('EKInterface')
        StyleSheet.EK_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout1.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout1.setSpacing(20)
        self.vBoxLayout1.addWidget(self.banner)
        self.vBoxLayout1.setAlignment(Qt.AlignTop)

        self.vBoxLayout.setContentsMargins(20, 0, 20, 36)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)


    def ek_connect(self):
        self.vBoxLayout.addWidget(self.firstConnectCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.userCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.areaCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.powerCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.encoderCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.colorCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.powerSaveCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.fingerCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.addFingerCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.updateCard, alignment=Qt.AlignTop)

        self.vBoxLayout.addWidget(self.conectCard, alignment=Qt.AlignTop)
        self.vBoxLayout.addWidget(self.upDataButton, alignment=Qt.AlignTop)
        
        self.vBoxLayout1.addLayout(self.vBoxLayout, 0)
        

    def showWifiInput(self, isChecked):
        if isChecked:
            self.config_connect_flag = '1'
            self.conectCard.nav.wifiSwitchButton.setText('On')
            self.wifiCard.setVisible(True)
            self.vBoxLayout.insertWidget(self.vBoxLayout.count()-1, self.wifiCard, alignment=Qt.AlignTop)
            self.conectCard.nav.wireSwitchButton.setChecked(False)
            self.conectCard.nav.bleSwitchButton.setChecked(False)
            self.conectCard.nav.wireSwitchButton.setText('Off')
            self.conectCard.nav.bleSwitchButton.setText('Off')

        else:
            self.conectCard.nav.wifiSwitchButton.setText('Off')
            self.wifiCard.setVisible(False)
            self.vBoxLayout.removeWidget(self.wifiCard)
    

    def bleSwitchState(self, isChecked):
        if isChecked:
            self.config_connect_flag = '2'
            self.conectCard.nav.bleSwitchButton.setText('On')
            self.conectCard.nav.wireSwitchButton.setText('Off')
            self.conectCard.nav.wifiSwitchButton.setText('Off')
            self.conectCard.nav.wireSwitchButton.setChecked(False)
            self.conectCard.nav.wifiSwitchButton.setChecked(False)
            self.updateCard.switchButton.setText('Off')
            self.updateCard.switchButton.setChecked(False)
            self.wifiCard.setVisible(False)
            self.vBoxLayout.removeWidget(self.wifiCard)
        else:
            self.conectCard.nav.bleSwitchButton.setText('Off')
    
    def wireSwitchState(self, isChecked):
        if isChecked:
            self.config_connect_flag = '3'
            self.conectCard.nav.wireSwitchButton.setText('On')
            self.conectCard.nav.bleSwitchButton.setText('Off')
            self.conectCard.nav.wifiSwitchButton.setText('Off')
            self.conectCard.nav.bleSwitchButton.setChecked(False)
            self.conectCard.nav.wifiSwitchButton.setChecked(False)
            self.updateCard.switchButton.setText('Off')
            self.updateCard.switchButton.setChecked(False)
            self.wifiCard.setVisible(False)
            self.vBoxLayout.removeWidget(self.wifiCard)
        else:
            self.conectCard.nav.wireSwitchButton.setText('Off')

    def on_update_clicked(self):
        flag = self.config_check()
        if flag == 1:
            QTimer.singleShot(100, self.update_info)
        else:
            return

    def update_info(self):
        # 保存 InfoBar 的引用
        self.updating_info = InfoBar.info(
            title='正在同步中',
            content="请保持连接等待配置同步完成",
            orient=Qt.Horizontal,
            isClosable=False,  # 禁用手动关闭
            position=InfoBarPosition.BOTTOM,
            parent=self
        )
        # 使用 QTimer 延迟执行配置更新
        QTimer.singleShot(100, self._do_update)

    def config_check(self):
        # user name
        user_name = self.userCard.config_user
        # 检查用户名是否为纯英文
        if not user_name.isascii() or user_name == '':
            InfoBar.warning(
                title='配置错误',
                content="请输入正确的用户名（仅支持英文）",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
            return 0
        # 检测颜色选择是否为空，如果是则设置默认值为蓝色
        if self.colorCard.config_color == '':
            self.colorCard.config_color = '#0000FF'
        power_save_start = self.powerSaveCard.config_power_start
        power_save_end = self.powerSaveCard.config_power_end
        # 检查睡眠时间是否为空,为空则设置默认值
        if power_save_start == '':
            self.powerSaveCard.config_power_start = '20:00'
        if power_save_end == '':
            self.powerSaveCard.config_power_end = '09:30'
        # 检查指纹PIN码是否为空且x模式关闭
        if self.fingerCard.config_pin == '' and self.fingerCard.config_x_flag == '0':
            InfoBar.warning(
                title='配置错误',
                content="请设置指纹PIN码或开启X模式",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
            return 0
        # 检查x模式是否开启且x输入为空
        if self.fingerCard.config_x_flag == '1' and self.fingerCard.config_x_input == '':
            InfoBar.warning(
                title='配置错误',
                content="x模式开启时，请输入宏定义",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
            return 0
        # 检查wifi连接模式打卡并且wifi ssid和wifi密码为空
        if self.config_connect_flag == '1' and (self.wifiCard.config_wifi_ssid == '' or self.wifiCard.config_wifi_password == ''):
            InfoBar.warning(
                title='配置错误',
                content="WIFI连接模式开启时，请输入WIFI ssid和WIFI密码",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
            return 0
        # 检测三种连接模式是否开启
        if self.config_connect_flag == '0':
            InfoBar.warning(
                title='配置错误',
                content="请选择一种数据更新方式",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
            return 0
        return 1

    def _do_update(self):
        # user name
        self.config_info['user_name'] = self.userCard.config_user
        # area
        self.config_info['area_prov'] = self.areaCard.config_prov
        self.config_info['area_city'] = self.areaCard.config_city
        # power show
        self.config_info['power_show'] = self.powerCard.config_powerShow_flag
        # encoder
        self.config_info['encoder'] = self.encoderCard.config_encoder
        # LED color
        self.config_info['color'] = self.colorCard.config_color
        # power save
        self.config_info['power_save_start'] = self.powerSaveCard.config_power_start
        self.config_info['power_save_end'] = self.powerSaveCard.config_power_end
        self.config_info['power_deep_save'] = self.powerSaveCard.config_power_deep_flag
        # finger
        self.config_info['finger_pin'] = self.fingerCard.config_pin
        self.config_info['x_mode'] = self.fingerCard.config_x_flag
        self.config_info['x_input'] = self.fingerCard.config_x_input
        # auto update
        self.config_info['update'] = self.updateCard.config_update_flag
        # connect way
        self.config_info['connect'] = self.config_connect_flag
        self.config_info['wifi_ssid'] = self.wifiCard.config_wifi_ssid
        self.config_info['wifi_ps'] = self.wifiCard.config_wifi_password
        # finger buffer
        self.config_info['finger_id'] = list(self.addFingerCard.fingerBuffer.keys())
        self.config_info['finger_name'] = list(self.addFingerCard.fingerBuffer.values())

        self.config_check()

        self.updateConfigInfo()
        flag = self.uart.updateConfig(self.config_info)
        
        # 关闭更新中的提示
        if hasattr(self, 'updating_info'):
            self.updating_info.close()
        
        if flag == 1:
            InfoBar.success(
                title='同步成功',
                content="请使用你的EK3吧",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                title='同步失败',
                content="请保持连接并重新同步配置",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=6000,
                parent=self
            )
    
    # 同步配置到本地文件
    def updateConfigInfo(self):
        config_path = os.path.join(os.path.dirname(__file__), 'ek3.config')
        
        # 如果文件不存在,创建新文件并写入所有配置
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as f:
                for key, value in self.config_info.items():
                    f.write(f"{key}={value}\n")
        else:
            # 读取现有配置
            config_dict = {}
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        config_dict[key] = value
                        
            # 更新配置
            config_dict.update(self.config_info)
            
            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                for key, value in config_dict.items():
                    f.write(f"{key}={value}\n")

    # 开启应用时初始化上一次的配置
    def initConfigInfo(self):
        config_path = os.path.join(os.path.dirname(__file__), 'ek3.config')
        
        # 如果配置文件不存在则跳过
        if not os.path.exists(config_path):
            return
            
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=')
                    self.config_info[key] = value
        
        # 初始化页面设置
        # user name
        self.userCard.lineEdit.setText(self.config_info['user_name'])
        self.userCard.config_user = self.config_info['user_name']
        # area
        self.areaCard.comboProv.setCurrentText(self.config_info['area_prov'])
        self.areaCard.comboCity.setCurrentText(self.config_info['area_city'])
        self.areaCard.config_prov = self.config_info['area_prov']  
        self.areaCard.config_city = self.config_info['area_city'] 
        # power show
        if self.config_info['power_show'] == '1':
            self.powerCard.switchButton.setChecked(True)
            self.powerCard.switchButton.setText('On')
        else:
            self.powerCard.switchButton.setChecked(False)
            self.powerCard.switchButton.setText('Off')
        self.powerCard.config_powerShow_flag = self.config_info['power_show']
        # encoder
        if self.config_info['encoder'] == '0':
            self.encoderCard.combo.setCurrentText('音量控制')
        else:
            self.encoderCard.combo.setCurrentText('上下滑动')
        self.encoderCard.config_encoder = self.config_info['encoder']
        # LED color
        self.colorCard.config_color = self.config_info['color'] 
        # power save
        self.powerSaveCard.config_power_start = self.config_info['power_save_start']
        self.powerSaveCard.config_power_end = self.config_info['power_save_end'] 
        self.powerSaveCard.config_power_deep_flag = self.config_info['power_deep_save']
        if self.config_info['power_deep_save'] == '1':
            self.powerSaveCard.switchButton.setChecked(True)
            self.powerSaveCard.switchButton.setText('On')
        else:
            self.powerSaveCard.switchButton.setChecked(False)
            self.powerSaveCard.switchButton.setText('Off')
        # finger
        self.fingerCard.lineEdit.setText(self.config_info['finger_pin'] )
        if self.config_info['x_mode'] == '1':
            self.fingerCard.switchButton.setChecked(True)
            self.fingerCard.switchButton.setText('On')
            self.fingerCard.visible.setVisible(True)
            self.fingerCard.xLineEdit.setText(self.config_info['x_input'])
        else:
            self.fingerCard.switchButton.setChecked(False)
            self.fingerCard.switchButton.setText('Off')
            self.fingerCard.visible.setVisible(False)
        self.fingerCard.config_pin = self.config_info['finger_pin'] 
        self.fingerCard.config_x_flag = self.config_info['x_mode'] 
        self.fingerCard.config_x_input = self.config_info['x_input'] 
        # auto update
        self.updateCard.config_update_flag = self.config_info['update']
        if self.config_info['update'] == '1':
            self.updateCard.switchButton.setChecked(True)
            self.updateCard.switchButton.setText('On')
        else:
            self.updateCard.switchButton.setChecked(False)
            self.updateCard.switchButton.setText('Off')
        # connect way
        self.config_connect_flag = self.config_info['connect']
        if self.config_connect_flag == '1':
            self.conectCard.nav.wifiSwitchButton.setChecked(True)
            self.conectCard.nav.wifiSwitchButton.setText('On')
            self.wifiCard.setVisible(True)
            self.vBoxLayout.insertWidget(self.vBoxLayout.count()-2, self.wifiCard, alignment=Qt.AlignTop)
        else:
            self.wifiCard.setVisible(False)
            self.vBoxLayout.removeWidget(self.wifiCard)
            self.conectCard.nav.wifiSwitchButton.setChecked(False)
            self.conectCard.nav.wifiSwitchButton.setText('Off')
        if self.config_connect_flag == '2':
            self.conectCard.nav.bleSwitchButton.setChecked(True)
            self.conectCard.nav.bleSwitchButton.setText('On')
        else:
            self.conectCard.nav.bleSwitchButton.setChecked(False)
            self.conectCard.nav.bleSwitchButton.setText('Off')
        if self.config_connect_flag == '3':
            self.conectCard.nav.wireSwitchButton.setChecked(True)
            self.conectCard.nav.wireSwitchButton.setText('On')
        else:
            self.conectCard.nav.wireSwitchButton.setChecked(False)
            self.conectCard.nav.wireSwitchButton.setText('Off')
        self.wifiCard.config_wifi_ssid = self.config_info['wifi_ssid']
        self.wifiCard.config_wifi_password = self.config_info['wifi_ps']
        self.wifiCard.lineEdit.setText(self.config_info['wifi_ssid'])
        self.wifiCard.pdLineEdit.setText(self.config_info['wifi_ps'])
        # finger buffer
        if len(self.config_info['finger_id']) > 2:
            keyList = self.config_info['finger_id'][1:-1].split(', ')
            valueList = self.config_info['finger_name'][1:-1].split(', ')
            for i in range(len(keyList)):
                curNum = int(keyList[i])
                name = valueList[i][1:-1]
                self.addFingerCard.fingerCur.append(curNum)
                self.addFingerCard.fingerBuffer[curNum] = name
                button = TransparentToolButton(FIF.REMOVE)
                self.addFingerCard.removeButtonList[curNum] = button
                self.addFingerCard.removeButtonList[curNum].clicked.connect(partial(self.addFingerCard.removeFingerCard, curNum))
                layout = self.addFingerCard.getFingerCard(name, curNum)
                self.addFingerCard.fingerLayouts[curNum] = layout
                self.addFingerCard.groupLayout.addLayout(self.addFingerCard.fingerLayouts[curNum])
        