# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from abc import abstractmethod
from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from wxpst.model import mbox_wrapper, global_env


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

    @abstractmethod
    def row_count(self):
        pass
