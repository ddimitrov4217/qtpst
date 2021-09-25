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
        for col, width in enumerate((0, 200, 70, 50, 300)):
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
            code = x.prop['propCode']
            return code if not code.startswith('0x') else 'zzz-%s' % code

        self.props = sorted(props, key=sort_props_key)
        self.props_display = {}

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

        if index.row() not in self.props_display:
            pc = self.props[index.row()]
            value_type, _, _ = pc.value.pt_desc
            value_size = len(pc.value._buf)
            value = pc.value.get_value()

            if value_type == 'Binary':
                value = PropertyValue.BinaryValue(value.data)

            value = str(value)
            value = re.sub('[\r\n]', ' ', value)
            value = value[:64]

            value_size = '{0:,d}'.format(value_size)
            self.props_display[index.row()] = pc.prop['propCode'], value_type, value_size, value

        if role == Qt.DisplayRole:
            value = self.props_display[index.row()]
            return value[index.column()-1]

        if role == Qt.TextAlignmentRole:
            if index.column() == 3:
                return Qt.AlignRight

        return None
