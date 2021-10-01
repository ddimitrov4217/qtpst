# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from codecs import decode
import logging

from PyQt5.QtWidgets import QTextEdit
from readms.metapst import get_internet_code_page
from .. import temp_file

log = logging.getLogger(__name__)


def plain_text_widget(message):
    attr = message.dict.get('Body', None)
    if attr is not None:
        return PlainTextBody(attr.value)
    return None


def html_widget(message):
    if HtmlBody.find_html_attr(message) is not None:
        return HtmlBody(message)
    return None


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

    @staticmethod
    def find_html_attr(message):
        pc = message.dict.get('Html', None)
        ec = message.dict.get('InternetCodepage', None)
        if pc is not None and ec is not None:
            code_page = get_internet_code_page(ec.value)
            return decode(pc.value.data, code_page, 'replace')
        return None

    def __init__(self, message):
        super().__init__()
        self.message = message
        self.attachments = self.message.attachments
        self.text = self.find_html_attr(message)
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
