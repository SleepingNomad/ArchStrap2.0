import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from lib.app import MainWindow
import sys



class StartApp(QThread):
    def __init__(self):
        super().__init__()
        
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.win = MainWindow()
        self.win.show()
        self.app.exec()

if __name__ == '__main__':
    thread = StartApp()
    thread.start()
    thread.wait()
    thread.terminate()