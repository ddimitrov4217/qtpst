# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from sys import exit
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyle, QToolBar, QAction, QSplitter
from . pstfiles import PstFilesDialog
from . navigator import MboxNavigator
from . messages import MessagesList


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Архиви на имейл кутия')
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.resize(900, 500)

        toolbar = QToolBar('global actions')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.pstDialog = PstFilesDialog(self)
        btnOpen = QAction('Open', self)
        btnOpen.setStatusTip('Избор и отваряне на pst файл')
        btnOpen.triggered.connect(self.openPstFile)
        toolbar.addAction(btnOpen)

        self.navigator = MboxNavigator()
        self.messages = MessagesList()

        splitter = QSplitter(self)
        splitter.addWidget(self.navigator)
        splitter.addWidget(self.messages)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

    def openPstFile(self):
        self.pstDialog.chooseFile()


def main():
    app = QApplication([])
    ex = App()
    ex.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
