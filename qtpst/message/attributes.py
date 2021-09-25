# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt, QItemSelectionModel

from .. import AbstractFlatItemModel

log = logging.getLogger(__name__)


class AttributesList(QTreeView):
    def __init__(self, props):
        super().__init__()
        self.setModel(AttributesListModel(props))
        self.init_ui()

    def init_ui(self):
        self.setColumnHidden(0, True)
        for col, width in enumerate((0, 200, 70, 50, 300)):
            self.setColumnWidth(col, width)

        # TODO Общ style за цялата програма от едно място
        self.setStyleSheet("""
        QTreeView::item {
            padding-top: 2;
            padding-bottom: 2;
        }
        """)
        self.setAlternatingRowColors(True)

        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)


class AttributesListModel(AbstractFlatItemModel):
    def __init__(self, props):
        super().__init__()
        self.props = props
        log.debug('number of properties: %d', len(self.props))
        self.attrs_names = ('Код', 'Тип', 'Размер', 'Стойност',)
        # TODO Сортиране на атрибутите по кодовете им

    def row_count(self):
        return len(self.props)

    def columnCount(self, _parent):
        return len(self.attrs_names) + 1

    def headerData(self, section, _orientation, role):
        if role == Qt.DisplayRole:
            return list(self.attrs_names)[section-1]
        return None

    def data(self, index, role):
        if not index.isValid() or index.column() == 0:
            return None

        # TODO Изваждане на данните
        if role == Qt.DisplayRole:
            prop = self.props[index.row()]
            if index.column() == 1:
                return prop.prop['propCode']

        return None
