# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

# https://doc.qt.io/qtforpython/tutorials/basictutorial/widgets.html
# леко модифициран

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QFont, QPalette, QColor


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(300, 300)
    w.setWindowTitle('Тестова страничка')

    label = QLabel(w)
    # label.setText("<font color='red' size=5>Hello (здравейте) World (всички)!</font>")
    font = QFont()
    font.setFamily("Georgia")
    font.setPointSize(16)
    label.setFont(font)
    label.setText("Здравейте всички!")

    palette = QPalette()
    palette.setColor(QPalette.WindowText, QColor.fromRgb(210, 0, 0, 255))
    label.setPalette(palette)

    # label.setStyleSheet("QLabel { background-color:rgb(255,255,0); color:blue; }");

    label.show()
    w.show()

    app.exec()
