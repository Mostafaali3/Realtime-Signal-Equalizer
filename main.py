import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *


compile_qrc()
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Equalizer')
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())