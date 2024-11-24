from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("后台应用程序")
        self.setGeometry(100, 100, 300, 200)

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setToolTip("后台应用程序")

        # 创建托盘菜单
        menu = QMenu()
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # 隐藏主窗口
        # self.hide()

        # 定时器，模拟后台任务
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.background_task)
        self.timer.start(1000)  # 每秒执行一次

    def background_task(self):
        print("后台任务正在运行...")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec()