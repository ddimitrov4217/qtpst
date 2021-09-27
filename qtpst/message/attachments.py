# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from os import startfile
from zipfile import ZipFile
import logging

from PyQt5.QtWidgets import QTreeView, QWidget, QToolBar, QVBoxLayout, QAction
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QItemSelectionModel, pyqtSignal

from .. import AbstractFlatItemModel, temp_file

log = logging.getLogger(__name__)

# TODO Запис на приложения файл
# TODO Икони според типовете на файловете (поне да се различава файл от приложено съобщение)
# TODO Различаване на plain и S/MIME; може би не трябва да се извежда като файл


class AttachmentsListWidget(QWidget):
    key_pressed = pyqtSignal(int)

    def __init__(self, attachments):
        super().__init__()
        self.list = AttachmentsList(attachments)
        self.init_ui()
        self.file_dialog = None

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
            return self.list.model().attachments[selected[0].row()]
        QMessageBox.warning(
            self, 'Грешка', 'Моля изберете файл от списъка с приложени файлове',
            buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
        return None

    def save_attachment(self):
        selected = self.get_selected()
        if selected is not None:
            file_name = self.save_file_dialog(self.list.model().att_filename(selected))
            if file_name is not None:
                log.debug(file_name)
                log.debug(selected)
                # TODO Запис на файла

    def save_all_attachments(self):
        file_name = self.save_file_dialog('attachments.zip')
        if file_name is not None:
            with ZipFile(file_name, 'w') as zout:
                for att in self.list.model().attachments:
                    name = self.list.model().att_filename(att)
                    content = att.dict.get('AttachDataObject')
                    zout.writestr(name, content.value.data)

    def open_attachment(self):
        selected = self.get_selected()
        if selected is not None:
            log.debug(selected)
            content = selected.dict.get('AttachDataObject')
            refname = self.list.model().att_filename(selected)
            refname = temp_file.write_temp(content.value.data, refname)
            startfile(refname)

    def hande_enter(self, key):
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.open_attachment()

    def save_file_dialog(self, default_file_name=None):
        if self.file_dialog is None:
            self.file_dialog = QFileDialog(self)
            self.file_dialog.setOptions(QFileDialog.Options() | QFileDialog.DontUseNativeDialog)
            self.file_dialog.setWindowTitle('Запис на файл')
            self.file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            self.file_dialog.setFileMode(QFileDialog.AnyFile)
            self.file_dialog.setViewMode(QFileDialog.Detail)

        if default_file_name is not None:
            self.file_dialog.selectFile(default_file_name)

        if self.file_dialog.exec():
            file_names = self.file_dialog.selectedFiles()
            return file_names[0]
        return None

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
        for col, width in enumerate((0, 400, 80, 90, 20)):
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
            file_name = self.att_filename(attv)
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

    def att_filename(self, attv):
        return self.att_value(attv, 'DisplayName', 'AttachLongFilename', 'AttachFilename')
