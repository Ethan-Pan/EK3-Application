# coding: utf-8
from typing import List
from PySide6.QtCore import Qt, Signal, QEasingCurve, QUrl, QSize, QTimer
from PySide6.QtGui import QIcon, QDesktopServices, QColor
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow, MSFluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF

from .ek3_interface import EKInterface
from .setting_interface import SettingInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        # create sub interface
        self.ekInterface = EKInterface(self)
        self.settingInterface = SettingInterface(self)

        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        # start theme listener
        self.themeListener.start()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        self.addSubInterface(self.ekInterface, FIF.ALIGNMENT, self.tr('配置'), FIF.ALIGNMENT)
        # add custom widget to bottom
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), FIF.SETTING)
        
        self.navigationInterface.setCurrentItem(self.ekInterface.objectName())

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(":/gallery/images/logo_ek3_black.png"))
        self.setWindowTitle('EK HOME')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        language = cfg.get(cfg.language).value
        if language.name() == "zh_CN":
            QDesktopServices.openUrl(QUrl(ZH_SUPPORT_URL))
        else:
            QDesktopServices.openUrl(QUrl(EN_SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))
