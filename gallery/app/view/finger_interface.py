# coding:utf-8
from PySide6.QtCore import Qt,QUrl, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout
from qfluentwidgets import (SwitchButton, GroupHeaderCardWidget,LineEdit,  PasswordLineEdit, TransparentToolButton,LineEdit, PasswordLineEdit, IconWidget, CaptionLabel, BodyLabel, Flyout,InfoBarIcon,MessageBoxBase, SubtitleLabel,InfoBar,InfoBarPosition)
from qfluentwidgets import FluentIcon as FIF
from functools import partial
from ..connect.uart import UartConnect
import time

class FingerCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("指纹设置")
        self.setBorderRadius(15)
        self.lineEdit = PasswordLineEdit()
        self.config_pin = ''
        self.lineEdit.setFixedWidth(160)
        self.lineEdit.setPlaceholderText("输入PIN码")
        self.lineEdit.textChanged.connect(self.on_text_changed)
        self.addGroup(':/gallery/images/password.png', "密码设置", "请输入指纹对应的解锁密码", self.lineEdit)

        self.switchButton = SwitchButton(self.tr('Off'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)
        self.config_x_flag = '0'
        self.addGroup(':/gallery/images/x.png', "X键模式", "开启后指纹密码失效，由自定义宏按键代替", self.switchButton)

        self.xLineEdit = LineEdit()
        self.xLineEdit.setFixedWidth(160)
        self.xLineEdit.setPlaceholderText("比如：CTRL+F")
        self.config_x_input = ''
        self.xLineEdit.textChanged.connect(self.on_xInput_text_changed)


        self.visible = self.addGroup(':/gallery/images/x.png', "X键设置", "输入自定义宏按键, 比如：CTRL+F, WIN+L, F5, SHIFT+F10", self.xLineEdit)
        self.visible.setVisible(False)

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.config_x_flag = '1'
            self.switchButton.setText(self.tr('On'))
            self.visible.setVisible(True)
        else:
            self.config_x_flag = '0'
            self.switchButton.setText(self.tr('Off'))
            self.visible.setVisible(False)
    
    def on_text_changed(self, text):
        self.config_pin = text

    def on_xInput_text_changed(self, text):
        self.config_x_input = text


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('命名你的指纹'), self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText(self.tr('请输入你要录入的指纹名称'))
        self.urlLineEdit.setClearButtonEnabled(True)

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # change the text of button
        self.yesButton.setText(self.tr('确定'))
        self.cancelButton.setText(self.tr('取消'))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.urlLineEdit.textChanged.connect(self._validateUrl)

    def _validateUrl(self, text):
        self.yesButton.setEnabled(QUrl(text).isValid())

class AddFingerCard(GroupHeaderCardWidget):
    def __init__(self, uart:UartConnect, parent=None):
        super().__init__(parent)
        self.fingerMaxNums = 5
        self.fingerCur = []
        self.fingerBuffer = {}
        
        self.uart = uart
        # 先初始化列表
        self.removeButtonList = []
        self.fingerLayouts = []  # 存储布局引用
        
        # 创建5个删除按钮
        for i in range(self.fingerMaxNums):
            button = TransparentToolButton(FIF.REMOVE)
            self.removeButtonList.append(button)
            
        # 创建5个指纹布局
        for i in range(self.fingerMaxNums):
            layout = QHBoxLayout()
            self.fingerLayouts.append(layout)
            
        self.setTitle("指纹管理")
        self.setBorderRadius(15)
        self.hBoxLayout = QHBoxLayout()

        self.iconWidget = IconWidget(':/gallery/images/finger.png')
        self.titleLabel = BodyLabel('添加指纹')
        self.contentLabel = CaptionLabel('点击右侧加号添加要识别的指纹')
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

        self.addButton = TransparentToolButton(FIF.ADD)
        self.addButton.clicked.connect(self.addFingerCard)
        
        self.subLayout.addWidget(self.addButton)
        self.hBoxLayout.addLayout(self.subLayout)
        self.groupLayout.addLayout(self.hBoxLayout)

        self.groupLayout.addWidget(self.separator)
        
    def getFingerCard(self, name, curNum):
        hBoxLayout = QHBoxLayout()
        titleLabel = BodyLabel(name)
        contentLabel = CaptionLabel('点击右侧减号删除该指纹')
        textLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        contentLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        textLayout.addWidget(titleLabel)
        textLayout.addWidget(contentLabel)
        hBoxLayout.addLayout(textLayout)
        hBoxLayout.addStretch(1)

        hBoxLayout.setSpacing(15)
        hBoxLayout.setContentsMargins(24, 10, 24, 10)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        textLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subLayout.addWidget(self.removeButtonList[curNum])
        hBoxLayout.addLayout(subLayout)
        return hBoxLayout
    
    def showCustomDialog(self):
        w = CustomMessageBox(self.window())
        if w.exec():
            return w.urlLineEdit.text()
    
    def showFlyout(self, button):
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title='注意',
            content="最多可以存储5个指纹哦！",
            target=button,
            parent=self,
            isClosable=True
        )
    
    def showFingerGuide(self):
        InfoBar.info(
            title='录取指纹',
            content="请反复按压指纹模组，直到蓝灯熄灭",
            orient=Qt.Horizontal,
            isClosable=False,   # disable close button
            position=InfoBarPosition.TOP,
            duration=8000,
            parent=self
        )
        
    
    def showFingerDelete(self):
        InfoBar.warning(
            title='删除指纹',
            content="指纹已删除",
            orient=Qt.Horizontal,
            isClosable=False,   # disable close button
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
    
    def showFingerFailed(self):
        InfoBar.error(
            title='录取失败',
            content="请重新录取指纹",
            orient=Qt.Horizontal,
            isClosable=False,   # disable close button
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )


    def addFingerCard(self):
        if len(self.fingerCur) >= 5:
            self.addButton.setEnabled(False)
            self.showFlyout(self.addButton)
        else:
            for i in range(5):
                if i not in self.fingerCur:
                    curNum = i
                    self.fingerCur.append(curNum)
                    break
            
            self.showFingerGuide()
            print(f'录入指纹id:{curNum}')
            # 启动指纹录入线程
            enroll_thread = self.uart.finger_enroll(curNum)
            enroll_thread.finished.connect(lambda flag: self._handleEnrollResult(flag, curNum))
    
    def _handleEnrollResult(self, flag, curNum):
        print(f'finger flag:{flag}')
        if flag == 1:  # 录入成功
            name = self.showCustomDialog()
            self.fingerBuffer[curNum] = name
            self.addButton.setEnabled(True)
            button = TransparentToolButton(FIF.REMOVE)
            self.removeButtonList[curNum] = button
            self.removeButtonList[curNum].clicked.connect(partial(self.removeFingerCard, curNum))
            layout = self.getFingerCard(f'{name}', curNum)
            self.fingerLayouts[curNum] = layout
            self.groupLayout.addLayout(self.fingerLayouts[curNum])
        else:  # 录入失败或异常
            self.fingerCur.remove(curNum)  # 移除未成功录入的指纹ID
            InfoBar.error(
                title='录入失败',
                content="请重新录取指纹",
                orient=Qt.Horizontal,
                isClosable=False,   # disable close button
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
    
    def removeFingerCard(self, order):
        self.fingerCur.remove(order)
        self.fingerBuffer.pop(order)
        self.addButton.setEnabled(True)
        while self.fingerLayouts[order].count():
            item = self.fingerLayouts[order].takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    subItem = item.layout().takeAt(0)
                    if subItem.widget():
                        subItem.widget().deleteLater()
        self.groupLayout.removeItem(self.fingerLayouts[order])
        flag = self.uart.finger_delete(order)
        print(f'remove id:{order}, remove flag:{flag}')
        if flag == 1:
            self.showFingerDelete()

