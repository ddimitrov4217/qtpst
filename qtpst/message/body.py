# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from codecs import decode
import logging

from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from readms.metapst import get_internet_code_page
from .. import temp_file

log = logging.getLogger(__name__)


def plain_text_widget(message):
    attr = message.dict.get('Body', None)
    if attr is not None:
        body = PlainTextBody(attr.value)
        return BodyWidget(body, message)
    return None


def html_widget(message):
    if HtmlBody.find_html_attr(message) is not None:
        body = HtmlBody(message)
        return BodyWidget(body, message)
    return None


class BodyWidget(QWidget):
    def __init__(self, body, message):
        super().__init__()
        self.body = body
        self.heading = HtmlBodyHeading(message)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.body)
        self.setLayout(layout)


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


class HtmlBodyHeading(QTextEdit):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.message_attr = AttrMultiFind(self.message)
        self.setObjectName('bodyHtmlHeading')
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(50)
        self.setMaximumHeight(150)
        content = []
        content.append('<html><body><p>')
        self.append_sender(content)
        self.append_received(content)
        self.append_receivers(content)
        self.append_subject(content)
        content.append('</p></body></html>')
        self.setHtml(''.join(content))
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)

    def append_received(self, content):
        attr = self.message_attr.find_attr('MessageDeliveryTime')
        if attr is not None:
            content.append('<b>ReceivedDate: </b>')
            content.append('{0:%d.%m.%Y %H:%M:%S}'.format(attr.value))
            content.append('<br/>')

    def append_subject(self, content):
        attr = self.message_attr.find_attr('ConversationTopic')
        if attr is not None:
            content.append('<b>Subject: </b>')
            content.append(attr.value)
            content.append('<br/>')

    def append_receivers(self, content):
        if len(self.message.recipients) > 0:
            cont_cc = []
            cont_to = []
            for rcp in self.message.recipients:
                rcp_attrs = AttrMultiFind(rcp)
                name = rcp_attrs.find_attr('DisplayName')
                addr = rcp_attrs.find_attr('SmtpAddress')
                isto = rcp_attrs.find_attr('RecipientType')
                if isto is not None and isto.value == 1:
                    cont_to.append(self.format_email_addr(name, addr))
                else:
                    cont_cc.append(self.format_email_addr(name, addr))
            if len(cont_to) > 0:
                content.append('<b>To: </b>')
                content.append('; '.join(cont_to))
                content.append('<br/>')
            if len(cont_cc) > 0:
                content.append('<b>Cc: </b>')
                content.append('; '.join(cont_cc))
                content.append('<br/>')
        else:
            name_cc = self.message_attr.find_attr('DisplayCc')
            name_to = self.message_attr.find_attr('DisplayTo')
            if name_to is not None:
                content.append('<b>To: </b>')
                content.append(name_to.value)
                content.append('<br/>')
            if name_cc is not None:
                content.append('<b>Cc: </b>')
                content.append(name_cc.value)
                content.append('<br/>')

    def append_sender(self, content):
        name = self.message_attr.find_attr('SenderName', 'SentRepresentingName')
        addr = self.message_attr.find_attr('SenderSmtpAddress', 'SentRepresentingSmtpAddress')
        if name is not None or addr is not None:
            content.append('<b>From:</b>')
            content.append(self.format_email_addr(name, addr))
            content.append('<br/>')

    def format_email_addr(self, name, addr):
        result = []
        if name is not None:
            result.append(' %s' % name.value)
        if addr is not None:
            result.append(' &lt;%s&gt;' % addr.value)
        return ' '.join(result)


class AttrMultiFind():
    def __init__(self, attrs):
        self.attrs = attrs

    def find_attr(self, *names):
        for name in names:
            attr = self.attrs.dict.get(name, None)
            if attr is not None:
                return attr
        return None
