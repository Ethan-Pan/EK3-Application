from qfluentwidgets import (ComboBox,GroupHeaderCardWidget)


class EncoderCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("旋钮设置")
        self.setBorderRadius(15)
        self.config_encoder = '0'
        self.combo = ComboBox()
        self.combo.addItems(['音量控制', '上下滑动','无功能纯解压'])

        self.addGroup(':/gallery/images/rotate.png', "旋钮功能", "设置旋钮的功能", self.combo)

        self.combo.currentTextChanged.connect(self.on_combo_changed)
        
    def on_combo_changed(self, text):
        """当下拉框选项改变时触发"""
        if text == '音量控制':
            self.config_encoder = '0'
        elif text == '上下滑动':
            self.config_encoder = '1'
        else:
            self.config_encoder = '2'