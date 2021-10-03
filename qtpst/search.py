# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLineEdit, QAction, QToolButton, QStyle
from PyQt5.QtCore import Qt

from . import mbox_wrapper

log = logging.getLogger(__name__)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setMaximumHeight(24)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)

        act_search = QAction('Търси', self)
        act_search.setToolTip('Стартира търсенето; също става и с Enter в кутийката')
        act_search.triggered.connect(self.start_search)
        btn_search = QToolButton()
        btn_search.setDefaultAction(act_search)
        btn_search.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        btn_search.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        layout.addWidget(btn_search)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText('Потърсете нещо')
        self.txt_search.setMaxLength(50)
        self.txt_search.returnPressed.connect(self.start_search)
        layout.addWidget(self.txt_search)

        self.cbx_match_mode = QComboBox()
        self.cbx_match_mode.addItems(['Започва като', 'Съдържа', 'Точно като'])
        layout.addWidget(self.cbx_match_mode)

        self.cbx_apply_mode = QComboBox()
        self.cbx_apply_mode.addItems(['Коя да е дума', 'Всички думи'])
        layout.addWidget(self.cbx_apply_mode)

        self.setLayout(layout)

    def start_search(self):
        if mbox_wrapper.mbox is None:
            return

        text = self.txt_search.text()
        if text is not None and len(text) > 0:
            apply_mode = self.cbx_apply_mode.currentIndex()
            match_mode = self.cbx_match_mode.currentIndex()
            log.debug('%s, apply=%d, match=%d', self.txt_search.text(), apply_mode, match_mode)
            # TODO Изпълняване на търсенето
            # TODO Сигнализиране на navigator за промяната
