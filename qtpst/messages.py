# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import re
import logging

from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QStyledItemDelegate
from PyQt5.QtCore import Qt, QItemSelectionModel, pyqtSignal
from PyQt5.QtGui import QColor

from . import mbox_wrapper, AbstractFlatItemModel
from . message import AppMessageNid

log = logging.getLogger(__name__)


class MessagesList(QTreeView):
    key_pressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.opened_messages = []

    def initUI(self):
        self.setModel(MessagesListModel())
        self.setColumnHidden(0, True)
        for col, width in enumerate((50, 120, 70, 50, 100, 300)):
            self.setColumnWidth(col, width)

        self.setObjectName('messages')
        self.setAlternatingRowColors(True)
        self.doubleClicked.connect(self.handle_open)
        self.key_pressed.connect(self.hande_enter)
        self.setItemDelegateForColumn(3, CategoryDelegate(self))

    def set_nid(self, nid):
        self.model().set_nid(nid)
        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.scrollTo(ix, QAbstractItemView.EnsureVisible)

    def handle_open(self, index):
        nid = self.model().model_data[index.row()][0]
        app = AppMessageNid(nid)
        self.opened_messages.append(app)
        app.show()

    def hande_enter(self, key):
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_open(self.selectedIndexes()[0])

    def handle_close(self):
        for app in self.opened_messages:
            app.close()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())


class MessagesListModel(AbstractFlatItemModel):
    def __init__(self, nid=None):
        super().__init__()
        self.nid = nid
        self.rows = 0
        self.message_attr = (
            'MessageDeliveryTime', 'MessageSizeExtended', 'Keywords',
            'SenderName', 'ConversationTopic')
        self.message_attr_decor = (
            ('{0:%d.%m.%Y %H:%M:%S}', Qt.AlignLeft),
            ('{0:,d}', Qt.AlignRight),
            (None, Qt.AlignLeft),
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

        entry = self.model_data.get(index.row(), None)
        if entry is None:
            page_fault = index.row()//self.page_size
            self.load_page(page_fault)
            entry = self.model_data[index.row()]

        if role == Qt.DisplayRole:
            value = entry[index.column()]
            fmt = self.message_attr_decor[index.column()-1][0]
            if value is not None:
                value = fmt.format(value) if fmt is not None else str(value)
                return re.sub("[\r\n]", " ", value)
            else:
                return None

        if role == Qt.TextAlignmentRole:
            return self.message_attr_decor[index.column()-1][1]

        # TODO червени за например големите
        # TODO със Qt.BackgroundRole за тези които имат тагове
        if role == Qt.ForegroundRole:
            return QColor(0, 0, 0)

        if role == Qt.EditRole:
            return entry[index.column()]

        return None


class CategoryDelegate(QStyledItemDelegate):
    # TODO Цветни маркери по добавените в съобщението
    #      https://stackoverflow.com/questions/53059449/
    COLOR_MAP = {
        'виолетова': QColor(255, 128, 255),
        'жълта': QColor(255, 255, 128),
        'зелена': QColor(128, 255, 128),
        'оранжева': QColor(255, 192, 128),
        'синя': QColor(128, 128, 255),
        'червена': QColor(255, 96, 96),
    }

    def __init__(self, owner):
        super().__init__(owner)

    def paint(self, painter, option, index):
        value = index.data(Qt.EditRole)
        if value is not None and isinstance(value, list) and len(value) > 0:
            for col_desc in value:
                color = self.get_color(col_desc)
                if color is not None:
                    # TODO рисуване на квадратче с указания цвят
                    log.debug(color)
        super().paint(painter, option, index)  # XXX Отпада след като стане готово

    def get_color(self, desc):
        for name_, value_ in self.COLOR_MAP.items():
            if desc.lower().startswith(name_):
                return value_
        return None
