# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QItemSelectionModel, QSize

from wxpst.model import mbox_wrapper


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
