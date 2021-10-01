# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from os import listdir, path, stat
from datetime import datetime

import logging

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt

from . import mbox_wrapper, global_env, AbstractFlatItemModel

log = logging.getLogger(__name__)

# TODO Двойно цъкване да отваря избрания файл


def read_pst(pst_file):
    if pst_file is not None and (
            mbox_wrapper.pst_file is None or
            mbox_wrapper.pst_file != pst_file):
        mbox_wrapper.close_mbox()
        mbox_wrapper.open_mbox(pst_file)
        return True
    return False


class PstFilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.changed = False

    def setup_ui(self):
        self.setWindowTitle('Изберете pst файл')
        buttons = QDialogButtonBox.Open | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.open_file)
        self.buttonBox.rejected.connect(self.no_choise)
        self.layout = QVBoxLayout()

        self.body = QTreeView()
        self.body.setModel(PstFilesListModel())
        self.body.setColumnHidden(0, True)
        for col, width in enumerate((50, 150, 70, 100)):
            self.body.setColumnWidth(col, width)

        self.body.setObjectName('pstFiles')
        self.body.setAlternatingRowColors(True)

        self.layout.addWidget(self.body)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.resize(370, 300)

    def open_file(self):
        self.changed = False
        selected = self.body.selectedIndexes()
        if selected is not None:
            pstfile = self.body.model().data(selected[0], Qt.DisplayRole)
            self.changed = read_pst(pstfile)
            self.hide()

    def choose_file(self):
        self.refresh_list()
        self.exec()
        return self.changed

    def no_choise(self):
        self.changed = False
        self.hide()

    def refresh_list(self):
        self.body.model().load_model_data()
        found = self.body.model().find_mbox_pst_index()
        self.body.clearSelection()
        self.body.setCurrentIndex(found)
        self.body.scrollTo(found, QAbstractItemView.EnsureVisible)


class PstFilesListModel(AbstractFlatItemModel):
    def __init__(self):
        super().__init__()
        self.attrs_names = ('Име на файла', 'Размер [MB]', 'От дата')
        self.attrs_decor = (
            ('{0:s}', Qt.AlignLeft),
            ('{0:,.3f}', Qt.AlignRight),
            ('{0:%d.%m.%Y}', Qt.AlignLeft))
        self.model_data = None

    def load_model_data(self):
        pst_dir = global_env.config.get('app', 'pstmbox_dir')
        self.model_data = []

        for pst_file in listdir(pst_dir):
            if not pst_file.endswith(".pst"):
                continue
            statx = stat(path.join(pst_dir, pst_file))
            entry = (0, pst_file, statx.st_size/(1024.0*1024.0),
                     datetime.fromtimestamp(statx.st_mtime))
            self.model_data.append(entry)

    def find_mbox_pst_index(self):
        found = 0
        if mbox_wrapper.pst_file is not None:
            for ix_, entry in enumerate(self.model_data):
                if entry[1] == mbox_wrapper.pst_file:
                    found = ix_
                    break
        return self.createIndex(found, 0)

    def row_count(self):
        return len(self.model_data) if self.model_data is not None else 0

    def data(self, index, role):
        if not index.isValid() or index.column() == 0:
            return None

        entry = self.model_data[index.row()]
        value = entry[index.column()]

        if role == Qt.DisplayRole:
            fmt = self.attrs_decor[index.column()-1][0]
            return fmt.format(value) if value is not None else None

        if role == Qt.TextAlignmentRole:
            return self.attrs_decor[index.column()-1][1]

        return None
