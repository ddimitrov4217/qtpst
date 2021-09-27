# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from codecs import decode

import logging

from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QMainWindow, QStyle

from readms.metapst import get_internet_code_page

from . attributes import AttributesList
from . body import PlainTextBody, HtmlBody
from . model import MessageNid, MessageMsg
from . attachments import AttachmentsListWidget

from .. import app_css

log = logging.getLogger(__name__)


def create_widget_msg(msgfile):
    log.info(msgfile)
    attrs = MessageMsg(msgfile)
    attrs.dump_hier()
    return TopMessageWidget(attrs)


def create_widget_nid(nid):
    log.info(nid)
    attrs = MessageNid(nid)
    attrs.dump_hier()
    return TopMessageWidget(attrs)


class TopMessageWidget(QWidget):
    def __init__(self, attrs):
        super().__init__()
        self.message = attrs
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget(self)

        # TODO Добавяне на панел за body (rtf), ако има и може
        # TODO Добавяне на панел за приложените съобщения, ако има
        # TODO Обслужване на S/MIME имейли - съдържание и приложение файлове

        self.add_html_body(tabs)
        self.add_plain_text_body(tabs)
        self.add_attachments(tabs)
        self.add_attrs_lists(tabs)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.show()

    def add_attrs_lists(self, tabs):
        plainTabs = QTabWidget(self)
        plainTabs.setTabPosition(QTabWidget.North)
        plainTabs.addTab(AttributesList(self.message.properties), 'Съобщение')

        for eno, entry in enumerate(self.message.recipients):
            tabname = 'Получател %d' % (eno+1)
            plainTabs.addTab(AttributesList(entry.properties), tabname)
        for eno, entry in enumerate(self.message.attachments):
            tabname = 'Приложение %d' % (eno+1)
            plainTabs.addTab(AttributesList(entry.properties), tabname)

        tabs.addTab(plainTabs, 'Всички атрибути')

    def find_attr_by_name(self, name):
        for pc in self.attrs.properties:
            if pc.prop['propCode'] == name:
                return pc
        return None

    def add_plain_text_body(self, tabs):
        attr = self.message.dict.get('Body', None)
        if attr is not None:
            widget = PlainTextBody(attr.value)
            tabs.addTab(widget, 'Текст на съобщението')

    def add_html_body(self, tabs):
        pc = self.message.dict.get('Html', None)
        ec = self.message.dict.get('InternetCodepage', None)
        if pc is not None and ec is not None:
            code_page = get_internet_code_page(ec.value)
            body_html = decode(pc.value.data, code_page, 'replace')
            widget = HtmlBody(body_html, self.message.attachments)
            tabs.addTab(widget, 'Съобщението като HTML')

    def add_attachments(self, tabs):
        if self.message.attachments is not None and len(self.message.attachments) > 0:
            has_not_inline = False
            for att in self.message.attachments:
                hidden = att.dict.get('AttachmentHidden', None)
                if hidden is None or not hidden.value:
                    has_not_inline = True
                    break
            if has_not_inline:
                widget = AttachmentsListWidget(self.message.attachments)
                tabs.addTab(widget, 'Приложени файлове')


class AppMessage(QMainWindow):
    def init_ui(self):
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.setCentralWidget(self.message_panel)
        qapp = QApplication.instance()
        geometry = qapp.primaryScreen().availableGeometry()
        self.resize(geometry.width()*0.5, geometry.height()*0.7)
        self.setStyleSheet(app_css())


class AppMessageFile(AppMessage):
    def __init__(self, msgfile):
        super().__init__()
        self.message_panel = create_widget_msg(msgfile)
        self.setWindowTitle(msgfile)
        self.init_ui()


class AppMessageNid(AppMessage):
    def __init__(self, nid):
        super().__init__()
        self.message_panel = create_widget_nid(nid)
        self.setWindowTitle(str(nid))
        self.init_ui()
