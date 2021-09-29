# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from abc import abstractmethod
from os import path
from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from PyQt5.QtCore import Qt
from wxpst.model import mbox_wrapper, global_env, temp_file


class AbstractFlatItemModel(QAbstractItemModel):
    @staticmethod
    def parent(_child):
        # представлява плосък списък
        return QModelIndex()

    @staticmethod
    def hasChildren(parent):
        return not parent.isValid()

    def index(self, row, col, _parent=None):
        return self.createIndex(row, col)

    def rowCount(self, parent):
        if parent.isValid():
            return 0  # няма деца
        return self.row_count()

    def columnCount(self, _parent):
        return len(self.attrs_names) + 1

    def headerData(self, section, _orientation, role):
        if role == Qt.DisplayRole:
            return list(self.attrs_names)[section-1]
        return None

    @abstractmethod
    def row_count(self):
        raise NotImplementedError


def app_css():
    css_file = path.join(path.dirname(__file__), 'resources', 'app.css')
    with open(css_file, encoding='UTF-8') as fin:
        return fin.read()
