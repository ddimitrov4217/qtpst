# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from PyQt5.QtWidgets import (
    QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QStyle, QSplitter,
    QTreeView, QAbstractItemView)
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QItemSelectionModel

from mbox_helper import get_pst_folder_hierarchy


class MboxNavigator(QTreeWidget):
    def __init__(self, with_empty=True):
        super().__init__()
        self.with_empty = with_empty
        self.initUI()
        self.propagateNid = None

    def initUI(self):
        self.setColumnCount(4)
        for col, width in enumerate((220, 45, 45)):
            self.setColumnWidth(col, width)
        self.setHeaderLabels(['Папка', 'Съобщения', 'Директни', ''])
        self.loadTreeNodes()

    def loadTreeNodes(self):
        items = []
        self.data = dict()
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
            self.data[id(item)] = node

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
        self.currentItemChanged.connect(self.handle_item_clicked)

    def setPropagateNid(self, func):
        self.propagateNid = func

    def handle_item_clicked(self, current, _previous):
        node = self.data[id(current)]
        print('... select', node.name, node.nid['nid'])
        if self.propagateNid is not None:
            self.propagateNid(node.nid['nid'])


class MessagesListModel(QAbstractItemModel):
    def __init__(self, nid=None):
        super().__init__()
        self.nid = nid
        self.rows = 0
        self.fetched_all = False
        self.max_row_queried = set()  # XXX за проследяване

    def setNid(self, nid):
        # XXX забелязва се че вика първата и последната страница
        zx = list(self.max_row_queried); zx.sort()
        print('... self.max_row_queried: ', zx)
        self.max_row_queried = set()
        self.nid = nid
        self.beginResetModel()
        print('... MessagesListModel use nid:', self.nid)
        # TODO извичане на съобщенията
        self.rows = 1000
        self.endResetModel()

    def columnCount(self, parent):
        return 3

    def rowCount(self, parent):
        if parent.isValid():
            return 0  # няма деца
        if self.nid is None:
            return 0
        # TODO редовете до момента
        return self.rows

    def parent(self, child):
        # представлява плосък списък
        return QModelIndex()

    def hasChildren(self, parent):
        return not parent.isValid()

    def index(self, row, col, parent):
        idx = self.createIndex(row, col)
        return idx

    def headerData(self, section, orientation, role):
        # https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html
        # PySide6.QtCore.Qt.ItemDataRole
        if role == Qt.DisplayRole:
            return ('Първа колонка', 'Втора колонка', 'Трета колонка')[section]
        # if role == Qt.SizeHintRole:
        #    return QSize((1000, 20, 60)[section], 22)
        # print('headerData:', role)

    def data(self, index, role):
        if not index.isValid():
            return None
        self.max_row_queried.add(index.row())
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return '%d' % index.row()
            return '%d: ред: %d; колонка: %d' % (self.nid, index.row(), index.column())
        # print('data:', role)


class MessagesList(QTreeView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setModel(MessagesListModel())
        self.setColumnHidden(0, True)
        for col, width in enumerate((50, 200, 45)):
            self.setColumnWidth(col, width)

    def setNid(self, nid):
        self.model().setNid(nid)
        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.scrollTo(ix, QAbstractItemView.EnsureVisible)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Тест за зареждане на имейл съобщения')
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.resize(900, 500)
        self.navigator = MboxNavigator(False)
        self.messages = MessagesList()

        # https://zetcode.com/gui/pyqt5/layout/
        layout = QVBoxLayout()
        splitter = QSplitter(self)
        splitter.addWidget(self.navigator)
        splitter.addWidget(self.messages)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        self.navigator.setPropagateNid(self.messages.setNid)

        layout.addWidget(splitter)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
