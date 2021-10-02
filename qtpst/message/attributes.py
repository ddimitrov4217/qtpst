# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging
import re

from PyQt5.QtWidgets import QTreeView, QDialog, QTextEdit, QToolBar, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QStyle
from PyQt5.QtCore import Qt, QItemSelectionModel, pyqtSignal
from readms.readpst import PropertyValue

from .. import AbstractFlatItemModel
from .. import app_css
from . attachments import SaveDialog

log = logging.getLogger(__name__)


class AttributesList(QTreeView):
    key_pressed = pyqtSignal(int)

    def __init__(self, props, value_dialog=None):
        super().__init__()
        self.setModel(AttributesListModel(props))
        self.value_dialog = value_dialog
        self.init_ui()

    def init_ui(self):
        self.setColumnHidden(0, True)
        for col, width in enumerate((0, 200, 60, 70, 300)):
            self.setColumnWidth(col, width)

        self.setObjectName('attrsList')
        self.setAlternatingRowColors(True)
        self.key_pressed.connect(self.hande_enter)
        self.doubleClicked.connect(self.open_value_dialog)

        ix = self.model().createIndex(0, 0)
        self.selectionModel().select(ix, QItemSelectionModel.Select | QItemSelectionModel.Rows)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())

    def hande_enter(self, key):
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.open_value_dialog()

    def open_value_dialog(self):
        if self.value_dialog is None:
            return
        selected = self.selectedIndexes()
        attr = self.model().props[selected[0].row()]
        if attr.vtype == 'String' and attr.vsize >= 102 or attr.vtype in ('Binary', 'Object'):
            self.value_dialog.set_attribute(attr)
            self.value_dialog.exec()


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


class AttributeValueWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.attr = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle('Стойност на атрибут')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.resize(600, 300)
        layout = QVBoxLayout()
        toolbar = QToolBar()
        toolbar.setObjectName('attributeValueActions')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        self.btn_save = QPushButton('Запиши', self)
        self.btn_save.setToolTip('Записва стойността на атрибута във файл')
        self.btn_save.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btn_save.clicked.connect(self.save_attribute)
        hbox.addWidget(self.btn_save)

        btn_close = QPushButton('Затвори', self)
        btn_close.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        btn_close.clicked.connect(self.close)
        hbox.addWidget(btn_close)

        self.text = QTextEdit()
        self.text.setObjectName('attributeValueText')
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QTextEdit.WidgetWidth)

        layout.addWidget(self.text)
        layout.addLayout(hbox)
        self.setLayout(layout)
        self.setStyleSheet(app_css())

    def set_attribute(self, attr):
        self.attr = attr
        self.text.setPlainText(str(attr.value))
        self.btn_save.setEnabled(attr.vtype == 'Binary')

    def save_attribute(self):
        file_name = SaveDialog.open_dialog('%s.bin' % self.attr.code)
        if file_name is not None:
            with open(file_name, 'wb') as fout:
                fout.write(self.attr.value.data.tobytes())
