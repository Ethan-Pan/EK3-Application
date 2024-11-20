# coding:utf-8
from qfluentwidgets import (GroupHeaderCardWidget,LineEdit, PasswordLineEdit)

class WifiInterface(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("WIFI设置")
        self.setBorderRadius(15)
        self.config_wifi_ssid = ''
        self.config_wifi_password = ''
        self.lineEdit = LineEdit()
        self.lineEdit.textChanged.connect(self.on_ssid_changed)
        self.lineEdit.setFixedWidth(200)
        self.lineEdit.setPlaceholderText("WIFI SSID")

        self.addGroup(':/gallery/images/wifi_ssid.png', "WIFI SSID", "输入WiFi的名称", self.lineEdit)

        self.pdLineEdit = PasswordLineEdit()
        self.pdLineEdit.setFixedWidth(200)
        self.pdLineEdit.setPlaceholderText("WIFI PASSWORD")
        self.pdLineEdit.textChanged.connect(self.on_password_changed)
        self.addGroup(':/gallery/images/wifi_password.png', "WIFI PASSWORD", "请输入wifi密码", self.pdLineEdit)

    def on_ssid_changed(self, text):
        self.config_wifi_ssid = text
    
    def on_password_changed(self, text):
        self.config_wifi_password = text
