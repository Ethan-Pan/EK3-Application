# coding:utf-8
from qfluentwidgets import (SwitchButton, GroupHeaderCardWidget)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import (SwitchButton, GroupHeaderCardWidget,TimePicker, IconWidget, CaptionLabel, BodyLabel)

class PowerCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("电量设置")
        self.setBorderRadius(15)

        self.config_powerShow_flag = '0'
        self.switchButton = SwitchButton(self.tr('Off'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)

        self.addGroup(':/gallery/images/power.png', "表盘电量显示", "选择是否将电量实时显示在表盘上", self.switchButton)

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.config_powerShow_flag = '1'
            self.switchButton.setText(self.tr('On'))
        else:
            self.config_powerShow_flag = '0'
            self.switchButton.setText(self.tr('Off'))

class PowerSaveCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("省电设置")
        self.setBorderRadius(15)
        self.hBoxLayout = QHBoxLayout()

        self.iconWidget = IconWidget(':/gallery/images/liangping.png')
        self.titleLabel = BodyLabel('亮屏区间')
        self.contentLabel = CaptionLabel('EK3在非亮屏区间处于关机状态以节省电量')
        self.textLayout = QVBoxLayout()
        self.subLayout = QHBoxLayout()
        self.iconWidget.setFixedSize(20, 20)
        self.contentLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        self.textLayout.addWidget(self.titleLabel)
        self.textLayout.addWidget(self.contentLabel)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.textLayout)
        self.hBoxLayout.addStretch(1)

        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.setContentsMargins(24, 10, 24, 10)
        self.textLayout.setContentsMargins(0, 0, 0, 0)
        self.textLayout.setSpacing(0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.textLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timerStart = TimePicker()
        self.timerEnd = TimePicker()
        self.textLabel = BodyLabel('--')
        self.timerStart.setTime(QTime(9, 30))
        self.timerEnd.setTime(QTime(22, 00))
        self.subLayout.addWidget(self.timerStart)
        self.subLayout.addWidget(self.textLabel)
        self.subLayout.addWidget(self.timerEnd)
        self.hBoxLayout.addLayout(self.subLayout)
        self.groupLayout.addLayout(self.hBoxLayout)

        self.switchButton = SwitchButton(self.tr('Off'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)

        self.turnOffButton = SwitchButton(self.tr('On'))
        self.turnOffButton.setChecked(True)
        self.turnOffButton.checkedChanged.connect(self.onTurnOffCheckedChanged)

        self.addGroup(':/gallery/images/powerSleep.png', "夜间工作模式", "EK3夜间不会关机，仅处于息屏状态,功耗会增加，建议连线使用", self.turnOffButton)
        self.addGroup(':/gallery/images/deepSavePower.png', "深度省电模式", "屏幕关闭常亮显示", self.switchButton)

        self.timerStart.timeChanged.connect(self.onStartTimeChanged)
        self.timerEnd.timeChanged.connect(self.onEndTimeChanged)
        self.config_power_start = ''
        self.config_power_end = ''
        self.config_power_deep_flag = '0'
        self.config_power_night_flag = '1'
        
    def onStartTimeChanged(self):
        start_time = self.timerStart.time.toString('hh:mm')
        self.config_power_start = start_time

    def onEndTimeChanged(self):
        end_time = self.timerEnd.time.toString('hh:mm') 
        self.config_power_end = end_time

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.config_power_deep_flag = '1'
            self.switchButton.setText(self.tr('On'))
        else:
            self.config_power_deep_flag = '0'
            self.switchButton.setText(self.tr('Off'))

    def onTurnOffCheckedChanged(self, isChecked):
        if isChecked:
            self.config_power_night_flag = '1'
            self.turnOffButton.setText(self.tr('On'))
        else:
            self.config_power_night_flag = '0'
            self.turnOffButton.setText(self.tr('Off'))
