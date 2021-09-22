# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import re
import logging

from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt, QItemSelectionModel

from . import mbox_wrapper, AbstractFlatItemModel

log = logging.getLogger(__name__)


class MessagesList(QTreeView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setModel(MessagesListModel())
        self.setColumnHidden(0, True)
        for col, width in enumerate((50, 120, 70, 100, 300)):
            self.setColumnWidth(col, width)

    def set_nid(self, nid):
        self.model().set_nid(nid)
        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.scrollTo(ix, QAbstractItemView.EnsureVisible)


class MessagesListModel(AbstractFlatItemModel):
    def __init__(self, nid=None):
        super().__init__()
        self.nid = nid
        self.rows = 0
        self.message_attr = (
            'MessageDeliveryTime', 'MessageSizeExtended',
            'SenderName', 'ConversationTopic')
        self.message_attr_decor = (
            ('{0:%d.%m.%Y %H:%M:%S}', Qt.AlignLeft),
            ('{0:,d}', Qt.AlignRight),
            ('{0:s}', Qt.AlignLeft),
            ('{0:s}', Qt.AlignLeft))
        self.model_data = {}
        self.page_size = 20

    def set_nid(self, nid):
        self.nid = nid
        self.beginResetModel()
        self.rows = mbox_wrapper.mbox.count_messages(self.nid)
        log.debug(self.nid)
        self.model_data = {}
        self.endResetModel()

    def load_page(self, page):
        log.debug(page)
        for entry, message in enumerate(mbox_wrapper.mbox.list_messages(
                self.nid, self.message_attr,
                skip=page*self.page_size,
                page=self.page_size)):
            self.model_data[page*self.page_size+entry] = message

    def row_count(self):
        if self.nid is None:
            return 0
        return self.rows

    def columnCount(self, _parent):
        return len(self.message_attr) + 1

    def headerData(self, section, _orientation, role):
        # https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html
        # PySide6.QtCore.Qt.ItemDataRole
        if role == Qt.DisplayRole:
            return list(self.message_attr)[section-1]
        return None

    def data(self, index, role):
        if not index.isValid() or index.column() == 0:
            return None

        if role == Qt.DisplayRole:
            entry = self.model_data.get(index.row(), None)
            if entry is None:
                page_fault = index.row()//self.page_size
                self.load_page(page_fault)
                entry = self.model_data[index.row()]

            value = entry[index.column()]
            fmt = self.message_attr_decor[index.column()-1][0]
            if value is not None:
                value = fmt.format(value)
                return re.sub("[\r\n]", " ", value)
            else:
                return None

        if role == Qt.TextAlignmentRole:
            return self.message_attr_decor[index.column()-1][1]

        return None
