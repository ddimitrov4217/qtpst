# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

# https://www.guru99.com/pyqt-tutorial.html
# Beyond empty windows

import sys

from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QWidget


def dialog():
    mbox = QMessageBox()
    mbox.setText("Your allegiance has been noted")
    mbox.setDetailedText("You are now a disciple and subject of the all-knowing Guru")
    mbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    mbox.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(300, 300)
    w.setWindowTitle('Тестова страничка с диалог')

    label = QLabel(w)
    label.setText("Отвори диалога за преглед")
    label.move(100, 130)
    label.show()

    btn = QPushButton(w)
    btn.setText('Отвори')
    btn.move(110, 150)
    btn.show()
    btn.clicked.connect(dialog)

    w.show()
    sys.exit(app.exec_())
