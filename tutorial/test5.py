# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

# https://doc.qt.io/qtforpython/tutorials/basictutorial/treewidget.html
# Displaying Data Using a Tree Widget

import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem

data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
        "Project B": ["file_b.csv", "photo.jpg"],
        "Project C": []}


if __name__ == '__main__':
    app = QApplication(sys.argv)

    tree = QTreeWidget()
    tree.setColumnCount(2)
    tree.setHeaderLabels(["Name", "Type"])

    items = []
    for key, values in data.items():
        item = QTreeWidgetItem([key])
        for value in values:
            ext = value.split(".")[-1].upper()
            child = QTreeWidgetItem([value, ext])
            item.addChild(child)
        items.append(item)

    tree.insertTopLevelItems(0, items)

    tree.resize(400, 300)
    tree.show()
    sys.exit(app.exec())
