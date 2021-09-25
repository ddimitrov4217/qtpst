# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QTextEdit

log = logging.getLogger(__name__)


class PlainTextBody(QTextEdit):
    def __init__(self, text):
        super().__init__()
        self.setPlainText(text)
        self.setup_ui()

    def setup_ui(self):
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        # TODO Общ стил на програмата
        self.setStyleSheet("""
        QTextEdit {
            font-family: Liberation Mono;
            font-size: 10pt;
        }
        """)


class HtmlBody(QTextEdit):
    def __init__(self, text, attachments):
        super().__init__()
        self.setHtml(text)
        self.attachments = attachments

    def setup_ui(self):
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        # TODO Извеждане на вложените картинки
