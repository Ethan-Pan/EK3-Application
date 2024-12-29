# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt, QTranslator, QSharedMemory
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.view.main_window import MainWindow


class SingleApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        self.shared_memory = QSharedMemory('ekhomeflag')  # 替换成你的应用唯一标识
        
        if self.shared_memory.attach():
            # 已经有一个实例在运行
            self.shared_memory.detach()
            sys.exit(1)
        
        # 创建共享内存
        if not self.shared_memory.create(1):
            sys.exit(1)

# 启用 DPI 缩放
if cfg.get(cfg.dpiScale) != "Auto":
    # 如果 DPI 缩放不是自动的,禁用 Qt 的高 DPI 缩放
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    # 设置自定义的 Qt 缩放因子
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

# 创建 QApplication 实例
# app = QApplication(sys.argv)
app = SingleApplication(sys.argv)
# 设置属性,不为原生小部件创建兄弟小部件
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# 国际化设置
# 获取配置的语言
locale = cfg.get(cfg.language).value
# 创建 FluentTranslator 实例
translator = FluentTranslator(locale)
# 创建 QTranslator 实例用于画廊翻译
galleryTranslator = QTranslator()
# 加载画廊翻译文件
galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

# 安装翻译器
app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# 创建并显示主窗口
w = MainWindow()
w.show()

# 运行应用程序事件循环
app.exec()
