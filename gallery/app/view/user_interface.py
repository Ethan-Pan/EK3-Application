# coding:utf-8
from qfluentwidgets import (GroupHeaderCardWidget,LineEdit)
from qfluentwidgets import FluentIcon as FIF


class UserCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("用户名设置")
        self.setBorderRadius(15)
        self.config_user = ''
        self.lineEdit = LineEdit()

        self.lineEdit.setFixedWidth(160)
        self.lineEdit.setPlaceholderText("暂时仅支持英文名")

        self.addGroup(':/gallery/images/user.png', "你的名字", "请输入你的名字以显示在设备上", self.lineEdit)
    
        self.lineEdit.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self, text):
        """当输入框内容改变时触发"""
        if text:
            self.config_user = text
