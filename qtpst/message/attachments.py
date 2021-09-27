# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt, QItemSelectionModel

from .. import AbstractFlatItemModel

log = logging.getLogger(__name__)

# TODO Запис на приложения файл
# TODO Запис на всички приложени файлове като zip
# TODO Отваряне на приложения файл с подходящата програма
# TODO Икони според типовете на файловете (поне да се различава файл от приложено съобщение)
# TODO Различаване на plain и S/MIME; може би не трябва да се извежда като файл


class AttachmentsList(QTreeView):
    def __init__(self, attachments):
        super().__init__()
        self.setModel(AttachmentsListModel(attachments))
        self.init_ui()

    def init_ui(self):
        self.setColumnHidden(0, True)
        for col, width in enumerate((0, 500, 80, 90, 20)):
            self.setColumnWidth(col, width)

        self.setObjectName('attachmentList')
        self.setAlternatingRowColors(True)

        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)


class AttachmentsListModel(AbstractFlatItemModel):
    def __init__(self, attachments):
        super().__init__()
        self.attachments = []
        self.display_values = {}

        for att in attachments:
            hidden = att.dict.get('AttachmentHidden', None)
            if hidden is None or not hidden.value:
                self.attachments.append(att)

        log.debug('number of attachemnts: %d/%d', len(self.attachments), len(attachments))
        self.attrs_names = ('Име на файла', 'Размер', 'Тип',)
        self.display_align = {2: Qt.AlignRight}

    def row_count(self):
        return len(self.attachments)

    def columnCount(self, _parent):
        return len(self.attrs_names) + 1

    def headerData(self, section, _orientation, role):
        if role == Qt.DisplayRole:
            return list(self.attrs_names)[section-1]
        return None

    def data(self, index, role):
        if not index.isValid() or index.column() == 0:
            return None

        if index.row() not in self.display_values:
            attv = self.attachments[index.row()]
            file_name = self.att_value(attv, 'DisplayName', 'AttachLongFilename', 'AttachFilename')
            mime_tag = self.att_value(attv, 'AttachMimeTag')
            att_object = attv.dict.get('AttachDataObject')
            self.display_values[index.row()] = file_name, '{0:,d}'.format(att_object.vsize), mime_tag

        if role == Qt.DisplayRole:
            return self.display_values[index.row()][index.column()-1]

        if role == Qt.TextAlignmentRole:
            return self.display_align.get(index.column(), Qt.AlignLeft)

        return None

    def att_value(self, attv, *alt_names):
        for attn in alt_names:
            result_att = attv.dict.get(attn, None)
            if result_att is not None and result_att.value is not None:
                return result_att.value
        return '--липсва--'
