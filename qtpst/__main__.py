# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from os import path
import traceback
import logging
import click

from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt5.QtWidgets import QStyle, QAction, QSplitter

from . import mbox_wrapper, global_env
from . pstfiles import PstFilesDialog, read_pst
from . navigator import MboxNavigator
from . messages import MessagesList
from . message import create_widget_msg

log = logging.getLogger(__name__)


class AppNavigator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.set_title()
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.resize(900, 500)

        toolbar = QToolBar('global actions')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.pstDialog = PstFilesDialog(self)
        btnOpen = QAction('Open', self)
        btnOpen.setStatusTip('Избор и отваряне на pst файл')
        btnOpen.triggered.connect(self.open_pst_file)
        toolbar.addAction(btnOpen)

        self.navigator = MboxNavigator()
        self.messages = MessagesList()
        self.navigator.set_propagation_nid(self.messages.set_nid)

        splitter = QSplitter(self)
        splitter.addWidget(self.navigator)
        splitter.addWidget(self.messages)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 9)
        self.setCentralWidget(splitter)

    def set_title(self):
        name = 'Архиви на имейл кутия'
        if mbox_wrapper.pst_file is not None:
            self.setWindowTitle('%s: %s' % (name, mbox_wrapper.pst_file))
        else:
            self.setWindowTitle(name)

    def open_pst_file(self):
        changed = self.pstDialog.choose_file()
        if changed:
            self.set_title()
            self.navigator.load_tree_nodes()


class AppMessage(QMainWindow):
    def __init__(self, msgfile):
        super().__init__()
        self.msgfile = msgfile
        self.message_panel = create_widget_msg(self.msgfile)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.msgfile)
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        self.setCentralWidget(self.message_panel)
        self.resize(700, 500)


def exception_hook(_etype, value, trace):
    text = traceback.format_tb(trace)
    text.insert(0, '%s\n' % value)
    text = ''.join(text)
    log.error(text)

    if QApplication.instance() is not None:
        dialog = QMessageBox.critical(
            None, 'Грешка', text,
            buttons=QMessageBox.Ignore | QMessageBox.Abort,
            defaultButton=QMessageBox.Ignore)

        if dialog == QMessageBox.Abort:
            sys.exit(127)


def run_navigator_app(pstfile):
    sys.excepthook = exception_hook
    qapp = QApplication([])
    app = AppNavigator()
    if pstfile is not None:
        read_pst(pstfile)
        app.set_title()
        app.navigator.load_tree_nodes()
    app.show()
    sys.exit(qapp.exec_())


def run_message_app(msgfile):
    sys.excepthook = exception_hook
    qapp = QApplication([])
    app = AppMessage(path.abspath(msgfile))
    app.show()
    sys.exit(qapp.exec_())


@click.group(name='qtpst', help='Четене на изпозлваните от MS Outlook файлове')
@click.option('--config', type=click.Path(exists=True), help='конфигурационен файл')
def cli(config=None):
    if config is None:
        config_file = path.join(path.dirname(__file__), '..', '..', 'wxpst')
        config_file = path.abspath(path.join(config_file, 'appconfig.ini'))
    else:
        config_file = config
    global_env.setup_env(config_file)


@cli.command(name='navigator', help='Избор и разглеждане на pst файлове')
@click.option('--file', type=click.Path(exists=True), help='pst файл за разглеждане')
def navigator(file):
    mbox_wrapper.init_mbox_wrapper(global_env.config)
    run_navigator_app(file)


@cli.command(name='message', help='Избор и разглеждане на msg файл')
@click.option('--file', type=click.Path(exists=True), help='msg файл за разглеждане')
def message(file):
    mbox_wrapper.init_mbox_wrapper(global_env.config)
    run_message_app(file)


if __name__ == '__main__':
    cli()
