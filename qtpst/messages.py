# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging
import re

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QPoint, QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QAbstractItemView, QStyledItemDelegate

from qtpst import AbstractFlatItemModel, TreeViewBase, mbox_wrapper
from qtpst.message import AppMessageNid

log = logging.getLogger(__name__)

# TODO: Колонка с индикатор за приложен файл


class MessagesList(TreeViewBase):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.opened_messages = []

    def init_ui(self):
        self.setModel(MessagesListModel())
        self.setColumnHidden(0, True)
        for col, width in enumerate((50, 120, 70, 50, 100, 300)):
            self.setColumnWidth(col, width)

        self.setObjectName('messages')
        self.setAlternatingRowColors(True)
        self.doubleClicked.connect(self.handle_open)
        self.enter_pressed.connect(self.handle_open)
        self.setItemDelegateForColumn(3, CategoryDelegate(self))
        self.setSortingEnabled(True)

    def set_nid(self, nid):
        self.model().set_nid(nid)
        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.scrollTo(ix, QAbstractItemView.EnsureVisible)

    def handle_open(self):
        index = self.selectedIndexes()[0]
        nid = self.model().model_data[index.row()][0]
        app = AppMessageNid(nid)
        self.opened_messages.append(app)
        app.show()

    def handle_close(self):
        for app in self.opened_messages:
            app.close()


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
        self.order_by = None
        self.order_reverse = True

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
                page=self.page_size,
                order_by=self.order_by,
                order_reverse=self.order_reverse)):
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
            return None

        if role == Qt.TextAlignmentRole:
            return self.message_attr_decor[index.column()-1][1]

        # TODO: червени за например големите
        # TODO: със Qt.BackgroundRole за тези които имат тагове
        if role == Qt.ForegroundRole:
            return QColor(0, 0, 0)

        if role == Qt.EditRole:
            return entry[index.column()]

        return None

    def sort(self, column, order):
        if self.nid is not None:
            self.order_by = self.message_attr[column-1]
            self.order_reverse = order == Qt.AscendingOrder
            log.debug('%s, %s', self.order_by, self.order_reverse)
            self.set_nid(self.nid)


class CategoryDelegate(QStyledItemDelegate):
    # https://stackoverflow.com/questions/53059449/
    COLOR_MAP = {
        'виолетова': QColor(255, 128, 255),
        'жълта': QColor(255, 255, 128),
        'зелена': QColor(128, 255, 128),
        'оранжева': QColor(255, 192, 128),
        'синя': QColor(128, 128, 255),
        'червена': QColor(255, 96, 96),
    }
    MARKER_WIDTH = 7
    MARKER_GAP = 2

    def paint(self, painter, option, index):
        value = index.data(Qt.EditRole)
        super().paint(painter, option, QModelIndex())
        if value is not None and isinstance(value, list) and len(value) > 0:
            rect = option.rect
            rect.translate(QPoint(self.MARKER_GAP + 1, 0))
            for col_desc in value:
                color = self.get_color(col_desc)
                if color is not None:
                    self.draw_mark(painter, color, rect)
                    rect.translate(QPoint(self.MARKER_WIDTH + self.MARKER_GAP + 1, 0))

    def draw_mark(self, painter, color, rect):
        painter.save()
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(0, 0, 0))

        brush = QBrush()
        brush.setColor(color)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        top = rect.topLeft()
        painter.drawRects(QRect(
            top + QPoint(0, self.MARKER_GAP),
            top + QPoint(self.MARKER_WIDTH, rect.height()-self.MARKER_GAP-5)))

        painter.restore()

    def get_color(self, desc):
        for name_, value_ in self.COLOR_MAP.items():
            if desc.lower().startswith(name_):
                return value_
        return None
