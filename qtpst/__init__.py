# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from abc import abstractmethod
from os import path
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QToolButton, QTreeView
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


def create_tool_button(widget, action, sp_style):
    btn = QToolButton()
    btn.setDefaultAction(action)
    btn.setIcon(widget.style().standardIcon(sp_style))
    btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    return btn


class TreeViewBase(QTreeView):
    enter_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.enter_pressed.emit()
