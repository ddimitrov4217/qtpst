# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from os import path

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from wxpst.model import mbox_wrapper, global_env


def init_mbox():
    config_file = path.join(path.dirname(__file__), '..', '..', 'wxpst')
    config_file = path.abspath(path.join(config_file, "appconfig.ini"))
    global_env.setup_env(config_file)
    mbox_wrapper.init_mbox_wrapper(global_env.config)


def read_pst(pst_file):
    mbox_wrapper.close_mbox()
    mbox_wrapper.open_mbox(pst_file)


class PstFilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('Изберете pst файл')
        buttons = QDialogButtonBox.Open | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.openFile)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        # TODO Извеждане на списъка с pst файлове за избор
        body = QLabel('TODO: Списък с pst файлове за избор')
        self.layout.addWidget(body)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def openFile(self):
        # TODO Намиране на избрания файл
        # TODO Прихващане на грешките за PyQt
        pstfile = '2020.pst'
        read_pst(pstfile)
        self.hide()

    def chooseFile(self):
        # TODO Обновяване на списъка с pst файловете
        self.open()


init_mbox()
