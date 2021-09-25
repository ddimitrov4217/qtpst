# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from PyQt5.QtWidgets import QWidget

log = logging.getLogger(__name__)


def create_widget_msg(msgfile):
    attrs = None  # TODO Прочитане на файла до обща структура с атрибути
    log.info(msgfile)
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
        # TODO Добавяне на панели за атрибутите
        # TODO Добавяне на панел за body (text), ако има
        # TODO Добавяне на панел за body (html), ако има
        # TODO Добавяне на панел за body (rtf), ако има и може
        # TODO Добавяне на панел за приложените файлове, ако има
        # TODO Добавяне на панел за приложените съобщения, ако има
        self.show()
