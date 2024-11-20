from qfluentwidgets import (SwitchButton, GroupHeaderCardWidget)

class UpdateCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("更新设置")
        self.setBorderRadius(15)

        self.config_update_flag = '0'
        self.switchButton = SwitchButton(self.tr('Off'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)

        self.addGroup(':/gallery/images/update.png', "自动更新检测", "EK3更新需要在wifi连接模型下运行", self.switchButton)

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.config_update_flag = '1'
            self.switchButton.setText(self.tr('On'))
        else:
            self.config_update_flag = '0'
            self.switchButton.setText(self.tr('Off'))
