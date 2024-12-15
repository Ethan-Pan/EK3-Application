from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import (IconWidget, CaptionLabel, BodyLabel, ComboBox, GroupHeaderCardWidget)



class AreaCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("地区设置")
        self.setBorderRadius(15)
        self.hBoxLayout = QHBoxLayout()

        self.iconWidget = IconWidget(':/gallery/images/location.png')
        self.titleLabel = BodyLabel('地区选择')
        self.contentLabel = CaptionLabel('选择你所在的城市和地区以更新天气信息')
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

        self.comboProv = ComboBox()
        self.comboProv.addItems(['广东','陕西', '浙江'])
        self.comboCity = ComboBox()
        self.comboCity.addItems(['深圳', '东莞', '广州', '惠州', '中山'])
        self.config_prov = '广东'
        self.config_city = '深圳'

        self.subLayout.addWidget(self.comboProv)
        self.subLayout.addWidget(self.comboCity)
        self.hBoxLayout.addLayout(self.subLayout)
        self.groupLayout.addLayout(self.hBoxLayout)
    
        self.comboProv.currentTextChanged.connect(self.on_prov_changed)
        self.comboCity.currentTextChanged.connect(self.on_city_changed)
        
    def on_prov_changed(self, text):
        """当省份选择改变时触发"""
        if text == '广东':
            self.comboCity.clear()
            self.comboCity.addItems(['深圳', '东莞', '广州', '惠州', '中山'])
        elif text == '陕西':
            self.comboCity.clear()
            self.comboCity.addItems(['西安'])
        elif text == '浙江':
            self.comboCity.clear()
            self.comboCity.addItems(['杭州'])
        self.config_prov = text
        
    def on_city_changed(self, text):
        """当城市选择改变时触发"""
        self.config_city = text