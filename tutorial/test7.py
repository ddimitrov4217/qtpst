# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from PyQt5.QtWidgets import (
    QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QStyle)
from PyQt5.QtCore import Qt

from mbox_helper import get_pst_folder_hierarchy


class MboxNavigator(QTreeWidget):
    def __init__(self, with_empty=True):
        super().__init__()
        self.with_empty = with_empty
        self.initUI()

    def initUI(self):
        self.setColumnCount(4)
        for col, width in enumerate((250, 45, 45)):
            self.setColumnWidth(col, width)
        self.setHeaderLabels(['Папка', 'Съобщения', 'Директни', ''])
        self.loadTreeNodes()

    def loadTreeNodes(self):
        items = []
        # https://www.pythonguis.com/faq/built-in-qicons-pyqt/
        icon = self.style().standardIcon(QStyle.SP_DirIcon)

        def get_total_messages(node):
            result = node.mcnt
            for cx in node.children:
                result += get_total_messages(cx)
            return result

        def add_node(node, parent=None):
            tcnt = get_total_messages(node)
            if not self.with_empty and tcnt == 0:
                return

            item = QTreeWidgetItem()
            item.setText(0, node.name)
            item.setText(1, '%d' % tcnt if tcnt > 0 else '')
            item.setText(2, '%d' % node.mcnt if node.mcnt > 0 else '')
            item.setTextAlignment(1, Qt.AlignRight)
            item.setTextAlignment(2, Qt.AlignRight)
            item.setIcon(0, icon)

            if parent is not None:
                parent.addChild(item)
            else:
                items.append(item)
            for node in node.children:
                add_node(node, item)

        for node in get_pst_folder_hierarchy():
            add_node(node)

        self.insertTopLevelItems(0, items)
        self.expandAll()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Тест за зареждане на имейл съобщения')
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.resize(400, 500)
        self.navigator = MboxNavigator(False)

        # https://zetcode.com/gui/pyqt5/layout/
        layout = QVBoxLayout()
        layout.addWidget(self.navigator)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
