# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
import traceback
import logging

from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt5.QtWidgets import QStyle, QAction, QSplitter

from . pstfiles import PstFilesDialog
from . navigator import MboxNavigator
from . messages import MessagesList

log = logging.getLogger(__name__)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.set_title()
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

    def set_title(self):
        name = 'Архиви на имейл кутия'
        if mbox_wrapper.pst_file is not None:
            self.setWindowTitle('%s: %s' % (name, mbox_wrapper.pst_file))
        else:
            self.setWindowTitle(name)

    def openPstFile(self):
        self.pstDialog.chooseFile()


def exception_hook(_etype, value, trace):
    text = traceback.format_tb(trace)
    text.insert(0, '%s\n' % value)
    text = ''.join(text)
    log.error(text)

    if QApplication.instance() is not None:
        dialog = QMessageBox.critical(
            None, 'Грешка', text,
            buttons=QMessageBox.Ignore | QMessageBox.Abort,
            defaultButton=QMessageBox.Ignore)

        if dialog == QMessageBox.Abort:
            sys.exit(127)


def main():
    sys.excepthook = exception_hook
    app = QApplication([])
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
