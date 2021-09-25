# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from readms.readmsg import PropertiesStream, Message, Attachment
from . attributes import AttributesList
from . body import PlainTextBody, HtmlBody

log = logging.getLogger(__name__)


def dump_attrs(attrs):
    def dump_entry(entry, level=0):
        name = '%s%s' % ('  '*level, entry.__class__.__name__)
        log.debug('%-19s%4d %s', name, len(entry.properties), entry.name)

        if isinstance(entry, Message):
            for re_ in entry.recipients:
                dump_entry(re_, level+1)
            for re_ in entry.attachments:
                dump_entry(re_, level+1)

        if isinstance(entry, Attachment):
            if entry.message is not None:
                dump_entry(entry.message, level+1)

    dump_entry(attrs)


def create_widget_msg(msgfile):
    log.info(msgfile)
    with PropertiesStream(msgfile) as ole:
        attrs = Message(ole, ole.root)
        dump_attrs(attrs)
    return TopMessageWidget(attrs)


def create_widget_nid(nid):
    attrs = None  # TODO Прочитане на nid до обща структура с атрибути
    log.info(nid)
    return TopMessageWidget(attrs)


class TopMessageWidget(QWidget):
    def __init__(self, attrs):
        super().__init__()
        self.attrs = attrs
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget(self)

        # TODO Добавяне на панел за body (rtf), ако има и може
        # TODO Добавяне на панел за приложените файлове, ако има
        # TODO Добавяне на панел за приложените съобщения, ако има

        self.add_plain_text_body(tabs)
        self.add_html_body(tabs)
        self.add_attrs_lists(tabs)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.show()

    def add_attrs_lists(self, tabs):
        plainTabs = QTabWidget(self)
        plainTabs.setTabPosition(QTabWidget.North)
        plainTabs.addTab(AttributesList(self.attrs.properties), 'Съобщение')

        for eno, entry in enumerate(self.attrs.recipients):
            tabname = 'Получател %d' % (eno+1)
            plainTabs.addTab(AttributesList(entry.properties), tabname)
        for eno, entry in enumerate(self.attrs.attachments):
            tabname = 'Приложение %d' % (eno+1)
            plainTabs.addTab(AttributesList(entry.properties), tabname)

        tabs.addTab(plainTabs, 'Всички атрибути')

    def find_attr_by_name(self, name):
        for pc in self.attrs.properties:
            if pc.prop['propCode'] == name:
                return pc
        return None

    def add_plain_text_body(self, tabs):
        pc = self.find_attr_by_name('Body')
        if pc is not None:
            widget = PlainTextBody(pc.value.get_value())
            tabs.addTab(widget, 'Текст на съобщението')

    def add_html_body(self, tabs):
        pc = self.find_attr_by_name('Html')
        if pc is not None:
            widget = HtmlBody(pc.value.get_value())
            tabs.addTab(widget, 'Съобщението ато HTML')
