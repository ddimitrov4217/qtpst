# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from readms.readmsg import PropertiesStream, Message, Attachment
from . attributes import AttributesList

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
        self.add_attrs_lists(tabs)

        # TODO Добавяне на панел за body (text), ако има
        # TODO Добавяне на панел за body (html), ако има
        # TODO Добавяне на панел за body (rtf), ако има и може
        # TODO Добавяне на панел за приложените файлове, ако има
        # TODO Добавяне на панел за приложените съобщения, ако има

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

        self.show()

    def add_attrs_lists(self, tabs):
        tabs.addTab(AttributesList(self.attrs.properties), 'Съобщение')
        for eno, entry in enumerate(self.attrs.recipients):
            tabname = 'Получател %d' % (eno+1)
            tabs.addTab(AttributesList(entry.properties), tabname)
