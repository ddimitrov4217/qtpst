# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QTreeView, QWidget, QToolBar, QVBoxLayout, QAction, QMessageBox
from PyQt5.QtCore import Qt, QItemSelectionModel, pyqtSignal

from .. import AbstractFlatItemModel

log = logging.getLogger(__name__)

# TODO Запис на приложения файл
# TODO Запис на всички приложени файлове като zip
# TODO Отваряне на приложения файл с подходящата програма
# TODO Икони според типовете на файловете (поне да се различава файл от приложено съобщение)
# TODO Различаване на plain и S/MIME; може би не трябва да се извежда като файл


class AttachmentsListWidget(QWidget):
    key_pressed = pyqtSignal(int)

    def __init__(self, attachments):
        super().__init__()
        self.list = AttachmentsList(attachments)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        toolbar = QToolBar()
        toolbar.setObjectName('attachmentActions')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        btn_open = QAction('Отвори', self)
        btn_open.setStatusTip('Отваря избрания файл с подходяща програма')
        btn_open.triggered.connect(self.open_attachment)
        self.key_pressed.connect(self.hande_enter)
        self.list.doubleClicked.connect(self.open_attachment)
        toolbar.addAction(btn_open)

        btn_save = QAction('Запиши', self)
        btn_save.setStatusTip('Записва избрания файл')
        btn_save.triggered.connect(self.save_attachment)
        toolbar.addAction(btn_save)

        btn_save_all = QAction('Запиши всички', self)
        btn_save_all.setStatusTip('Записва всички приложени файлове в zip')
        btn_save_all.triggered.connect(self.save_all_attachments)
        toolbar.addAction(btn_save_all)

        layout.addWidget(toolbar)
        layout.addWidget(self.list)
        self.setLayout(layout)

    def get_selected(self):
        selected = self.list.selectedIndexes()
        if selected is not None and len(selected) > 0:
            return self.list.model().display_values[selected[0].row()]
        QMessageBox.warning(
            self, 'Грешка', 'Моля изберете файл от списъка с приложени файлове',
            buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
        return None

    def save_attachment(self):
        selected = self.get_selected()
        if selected is not None:
            file_name = selected[0]
            log.debug(file_name)
            # TODO Избор на папка с отваряне на диалог
            # TODO Запис на файла

    def save_all_attachments(self):
        log.debug('... all')
        # TODO Избор на папка
        # TODO Генериране на име на файла
        # TODO Пакетиране на всички файлове в zip
        # TODO Запис на файла

    def open_attachment(self):
        selected = self.get_selected()
        if selected is not None:
            log.debug(selected[0])
            # TODO Запис във временната директори
            # TODO Отваряне с rundll като за Ms-Windows
            pass

    def hande_enter(self, key):
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.open_attachment()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())


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
