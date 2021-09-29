# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging
import re

from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt, QItemSelectionModel
from readms.readpst import PropertyValue

from .. import AbstractFlatItemModel

log = logging.getLogger(__name__)


class AttributesList(QTreeView):
    def __init__(self, props):
        super().__init__()
        self.setModel(AttributesListModel(props))
        self.init_ui()

    def init_ui(self):
        self.setColumnHidden(0, True)
        for col, width in enumerate((0, 200, 60, 70, 300)):
            self.setColumnWidth(col, width)

        self.setObjectName('attrsList')
        self.setAlternatingRowColors(True)

        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)


class AttributesListModel(AbstractFlatItemModel):
    def __init__(self, props):
        super().__init__()
        log.debug('number of properties: %d', len(props))
        self.attrs_names = ('Код', 'Тип', 'Размер', 'Стойност',)

        def sort_props_key(x):
            return x.code if not x.code.startswith('0x') else 'zzz-%s' % x.code

        self.props = sorted(props, key=sort_props_key)
        self.props_display = {}

    def row_count(self):
        return len(self.props)

    def data(self, index, role):
        if not index.isValid() or index.column() == 0:
            return None

        if index.row() not in self.props_display:
            attv = self.props[index.row()]
            if not isinstance(attv.value, PropertyValue.BinaryValue):
                value = str(attv.value)
                value = re.sub('[\r\n]', ' ', value)
                value = value[:64]
            else:
                value = PropertyValue.BinaryValue(attv.value.data[:16])
                value = str(value)

            vsize = '{0:,d}'.format(attv.vsize)
            self.props_display[index.row()] = attv.code, attv.vtype, vsize, value

        if role == Qt.DisplayRole:
            value = self.props_display[index.row()]
            return value[index.column()-1]

        if role == Qt.TextAlignmentRole:
            if index.column() == 3:
                return Qt.AlignRight

        return None
