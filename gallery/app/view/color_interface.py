# coding:utf-8
from PySide6.QtCore import Qt
from qfluentwidgets import (PrimaryPushButton,GroupHeaderCardWidget,ColorDialog,PrimaryPushButton)



class ColorCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("灯光设置")
        self.setBorderRadius(15)

        self.config_color = ''
        self.button = PrimaryPushButton('选择颜色')
        self.button.clicked.connect(self.showColorDialog)

        self.addGroup(':/gallery/images/LED.png', "LED底色设置", "底色只在常亮模式与呼吸模式生效", self.button)

    def showColorDialog(self):
        w = ColorDialog(Qt.cyan, self.tr('Choose color'), self.window())
        w.colorChanged.connect(lambda c: self.update_coplor(c))
        w.exec()

    def update_coplor(self, c):
        self.config_color = c.name()