# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QTextEdit
from .. import temp_file

log = logging.getLogger(__name__)


class PlainTextBody(QTextEdit):
    def __init__(self, text):
        super().__init__()
        self.setPlainText(text)
        self.setup_ui()

    def setup_ui(self):
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setObjectName('plainMessage')


class HtmlBody(QTextEdit):
    # TODO Панел с информация за текущото съобщения; нещо като както е за Forward

    def __init__(self, text, attachments):
        super().__init__()
        self.attachments = attachments
        self.text = text
        self.setup_ui()
        self.setObjectName('bodyHtml')

    def setup_ui(self):
        body_html = self.text
        for att in self.attachments:
            cid = att.dict.get('AttachContentId', None)
            if cid is not None:
                content = att.dict.get('AttachDataObject')
                refname = temp_file.write_temp(content.value.data)
                body_html = body_html.replace('cid:%s' % cid.value, refname)
        self.setHtml(body_html)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
