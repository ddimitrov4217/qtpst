# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from wxpst.model import mbox_wrapper


def read_pst(pst_file):
    if pst_file is not None and (
            mbox_wrapper.pst_file is None or
            mbox_wrapper.pst_file != pst_file):
        mbox_wrapper.close_mbox()
        mbox_wrapper.open_mbox(pst_file)
        return True
    return False


class PstFilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.changed = False

    def setupUI(self):
        self.setWindowTitle('Изберете pst файл')
        buttons = QDialogButtonBox.Open | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.open_file)
        self.buttonBox.rejected.connect(self.no_choise)
        self.layout = QVBoxLayout()
        # TODO Извеждане на списъка с pst файлове за избор
        body = QLabel('TODO: Списък с pst файлове за избор')
        self.layout.addWidget(body)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def open_file(self):
        self.changed = False
        # TODO Намиране на избрания файл
        pstfile = '2020.pst'
        self.changed = read_pst(pstfile)
        self.hide()

    def choose_file(self):
        self.exec()
        return self.changed

    def no_choise(self):
        self.changed = False
        self.hide()
