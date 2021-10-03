# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from os import startfile, path
from zipfile import ZipFile
import logging

from PyQt5.QtWidgets import QTreeView, QWidget, QToolBar, QVBoxLayout, QAction
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QStyle
from PyQt5.QtCore import Qt, QItemSelectionModel, pyqtSignal

from .. import AbstractFlatItemModel, temp_file, create_tool_button

log = logging.getLogger(__name__)

# TODO Икони според типовете на файловете (поне да се различава файл от приложено съобщение)
# TODO Отваряне на вложено съобщения


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

        act_open = QAction('Отвори', self)
        act_open.setToolTip('Отваря избрания файл с подходяща програма')
        act_open.triggered.connect(self.open_attachment)
        self.key_pressed.connect(self.hande_enter)
        self.list.doubleClicked.connect(self.open_attachment)
        btn_open = create_tool_button(self, act_open, QStyle.SP_DialogOpenButton)
        toolbar.addWidget(btn_open)

        act_save = QAction('Запиши', self)
        act_save.setToolTip('Записва избрания файл')
        act_save.triggered.connect(self.save_attachment)
        btn_save = create_tool_button(self, act_save, QStyle.SP_DialogSaveButton)
        toolbar.addWidget(btn_save)

        act_save_all = QAction('Запиши всички', self)
        act_save_all.setToolTip('Записва всички приложени файлове в zip')
        act_save_all.triggered.connect(self.save_all_attachments)
        btn_save_all = create_tool_button(self, act_save_all, QStyle.SP_DialogSaveButton)
        toolbar.addWidget(btn_save_all)

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
            file_name = SaveDialog.open_dialog(self.list.model().att_filename(selected))
            if file_name is not None:
                with open(file_name, 'wb') as fout:
                    content = selected.dict.get('AttachDataObject')
                    fout.write(content.value.data)
                QMessageBox.information(
                    self, 'Информация',
                    'Файла [%s] е записан успешно.' % path.basename(file_name),
                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

    def save_all_attachments(self):
        file_name = SaveDialog.open_dialog('attachments.zip')
        if file_name is not None:
            with ZipFile(file_name, 'w') as zout:
                for att in self.list.model().attachments:
                    name = self.list.model().att_filename(att)
                    content = att.dict.get('AttachDataObject')
                    zout.writestr(name, content.value.data)
            QMessageBox.information(
                self, 'Информация',
                'Архива [%s] е записан успешно.' % path.basename(file_name),
                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

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

    @staticmethod
    def att_value(attv, *alt_names):
        for attn in alt_names:
            result_att = attv.dict.get(attn, None)
            if result_att is not None and result_att.value is not None:
                return result_att.value
        return '--липсва--'

    def att_filename(self, attv):
        return self.att_value(attv, 'DisplayName', 'AttachLongFilename', 'AttachFilename')


# pylint: disable=too-few-public-methods
# Класа е singleton за да се изпозлва винаги един и същ диалог за избор на файл за запис
class SaveDialog():
    dialog = None

    @classmethod
    def open_dialog(cls, default_file_name=None):
        if cls.dialog is None:
            cls.dialog = QFileDialog()
            cls.dialog.setOptions(QFileDialog.Options() | QFileDialog.DontUseNativeDialog)
            cls.dialog.setWindowTitle('Запис на файл')
            cls.dialog.setAcceptMode(QFileDialog.AcceptSave)
            cls.dialog.setFileMode(QFileDialog.AnyFile)
            cls.dialog.setViewMode(QFileDialog.Detail)

        if default_file_name is not None:
            cls.dialog.selectFile(default_file_name)

        if cls.dialog.exec():
            file_names = cls.dialog.selectedFiles()
            return file_names[0]

        return None
