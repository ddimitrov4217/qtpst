# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

# https://www.guru99.com/pyqt-tutorial.html

import sys
from PyQt5.QtWidgets import QApplication, QWidget
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(300, 300)
    w.setWindowTitle('Тестване на инсталацията')
    w.show()
    sys.exit(app.exec_())
