# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys

from mbox_helper import get_pst_folder_hierarchy
from PyQt5.QtCore import QAbstractItemModel, QItemSelectionModel, QModelIndex, QSize, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QSplitter,
    QStyle,
    QTreeView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from readms.pstwrap import mbox_wrapper


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
        self.message_attr = (
            'MessageSizeExtended', 'MessageDeliveryTime',
            'SenderName', 'ConversationTopic')
        self.message_attr_decor = (
            ('{0:,d}', Qt.AlignRight),
            ('{0:%d.%m.%Y %H:%M:%S}', Qt.AlignLeft),
            ('{0:s}', Qt.AlignLeft),
            ('{0:s}', Qt.AlignLeft))
        self.data = {}
        self.page_size = 20

    def setNid(self, nid):
        self.nid = nid
        self.beginResetModel()
        self.rows = mbox_wrapper.mbox.count_messages(self.nid)
        print('... MessagesListModel use nid:', self.nid)
        self.data = {}
        self.endResetModel()

    def loadPage(self, page):
        print('... load page:', page)
        for entry, message in enumerate(mbox_wrapper.mbox.list_messages(
                self.nid, self.message_attr,
                skip=page*self.page_size,
                page=self.page_size)):
            self.data[page*self.page_size+entry] = message

    def columnCount(self, parent):
        return len(self.message_attr) + 1

    def rowCount(self, parent):
        if parent.isValid():
            return 0  # няма деца
        if self.nid is None:
            return 0
        return self.rows

    def parent(self, child):
        # представлява плосък списък
        return QModelIndex()

    def hasChildren(self, parent):
        return not parent.isValid()

    def index(self, row, col, parent=None):
        idx = self.createIndex(row, col)
        return idx

    def headerData(self, section, orientation, role):
        # https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html
        # PySide6.QtCore.Qt.ItemDataRole
        if role == Qt.DisplayRole:
            return list(self.message_attr)[section-1]

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            entry = self.data.get(index.row(), None)
            if entry is None:
                page_fault = index.row()//self.page_size
                self.loadPage(page_fault)
                entry = self.data[index.row()]

            value = entry[index.column()]
            fmt = self.message_attr_decor[index.column()-1][0]
            return fmt.format(value) if value is not None else None

        if role == Qt.SizeHintRole:
            return QSize(0, 16)

        if role == Qt.TextAlignmentRole:
            return self.message_attr_decor[index.column()-1][1]

        # print('data:', role)


class MessagesList(QTreeView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setModel(MessagesListModel())
        self.setColumnHidden(0, True)
        for col, width in enumerate((50, 70, 120, 100, 300)):
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
