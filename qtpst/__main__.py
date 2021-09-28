# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from os import path
import traceback
import logging
import click

from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt5.QtWidgets import QStyle, QAction, QSplitter

from . import mbox_wrapper, global_env, app_css, temp_file
from . pstfiles import PstFilesDialog, read_pst
from . navigator import MboxNavigator
from . messages import MessagesList
from . message import AppMessageFile, AppMessageNid

log = logging.getLogger(__name__)


class AppNavigator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.set_title()
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        qapp = QApplication.instance()
        geometry = qapp.primaryScreen().availableGeometry()
        self.resize(geometry.width()*0.7, geometry.height()*0.7)

        toolbar = QToolBar('global actions')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.pstDialog = PstFilesDialog(self)
        btn_open = QAction('Open', self)
        btn_open.setToolTip('Избор и отваряне на pst файл')
        btn_open.triggered.connect(self.open_pst_file)
        toolbar.addAction(btn_open)

        btn_colored = QAction('Оцветени', self)
        btn_colored.setToolTip('Извежда само имейлите отбелязани с цветна категория')
        btn_colored.triggered.connect(self.filter_only_colored)
        toolbar.addAction(btn_colored)

        btn_clear = QAction('Изчисти филтрите', self)
        btn_clear.setToolTip('Изчиства всички приложени филтри')
        btn_clear.triggered.connect(self.filter_clear)
        toolbar.addAction(btn_clear)

        self.navigator = MboxNavigator()
        self.messages = MessagesList()
        self.navigator.set_propagation_nid(self.messages.set_nid)

        splitter = QSplitter(self)
        splitter.addWidget(self.navigator)
        splitter.addWidget(self.messages)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 9)
        self.setCentralWidget(splitter)
        self.setStyleSheet(app_css())

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

    def filter_only_colored(self):
        if mbox_wrapper.mbox is not None:
            found = mbox_wrapper.mbox.search_categories()
            self.navigator.load_tree_nodes(found['nid'])

    def filter_clear(self):
        if mbox_wrapper.mbox is not None:
            found = mbox_wrapper.mbox.set_filter(None)
            self.navigator.load_tree_nodes(found['nid'])

    def closeEvent(self, event):
        self.messages.handle_close()
        super().closeEvent(event)


def exception_hook(_etype, value, trace):
    text = traceback.format_tb(trace)
    text.insert(0, '%s\n' % value)
    text = ''.join(text)
    print(text, file=sys.stderr)

    if QApplication.instance() is not None:
        dialog = QMessageBox.critical(
            None, 'Грешка', text,
            buttons=QMessageBox.Ignore | QMessageBox.Abort,
            defaultButton=QMessageBox.Ignore)

        if dialog == QMessageBox.Abort:
            sys.exit(127)


def run_prepare():
    mbox_wrapper.init_mbox_wrapper(global_env.config)
    sys.excepthook = exception_hook
    return QApplication([])


def run_start(app, tapp):
    app.show()
    status = tapp.exec_()
    temp_file.cleanup()
    sys.exit(status)


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
    tapp = run_prepare()
    app = AppNavigator()
    if file is not None:
        read_pst(file)
        app.set_title()
        app.navigator.load_tree_nodes()
    run_start(app, tapp)


@cli.command(name='message', help='Избор и разглеждане на msg файл')
@click.argument('file', type=click.Path(exists=True))
@click.option('--nid', type=int, help='nid от pst файл')
def message(file, nid=None):
    tapp = run_prepare()
    if nid is not None:
        read_pst(file)
        app = AppMessageNid(nid)
    else:
        app = AppMessageFile(file)
    run_start(app, tapp)


if __name__ == '__main__':
    cli()
