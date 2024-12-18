# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

# https://data-flair.training/blogs/python-pyqt5-tutorial/
# How to Create a Window in Python PyQt5?

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

# from PyQt5.QtGui import QIcon


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Hello, world!'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('това тука е status bar ...')


def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
