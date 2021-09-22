# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from sys import exit
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QStyle


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Архиви на имейл кутия')
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.resize(900, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)


def main():
    app = QApplication([])
    ex = App()
    ex.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
