# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from os import path
import traceback
import logging
import click

from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt5.QtWidgets import QStyle, QAction, QSplitter, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from . import mbox_wrapper, global_env, app_css, temp_file, create_tool_button
from . pstfiles import PstFilesDialog, read_pst
from . navigator import MboxNavigator
from . messages import MessagesList
from . message import AppMessageFile, AppMessageNid
from . search import SearchWidget

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
        act_open = QAction('Open', self)
        act_open.setToolTip('Избор и отваряне на pst файл')
        act_open.triggered.connect(self.open_pst_file)
        btn_open = create_tool_button(self, act_open, QStyle.SP_DialogOpenButton)
        toolbar.addWidget(btn_open)

        act_colored = QAction('Оцветени', self)
        act_colored.setToolTip('Извежда само имейлите отбелязани с цветна категория')
        act_colored.triggered.connect(self.filter_only_colored)
        btn_colored = create_tool_button(self, act_colored, QStyle.SP_FileDialogInfoView)
        toolbar.addWidget(btn_colored)

        act_clear = QAction('Изчисти филтрите', self)
        act_clear.setToolTip('Изчиства всички приложени филтри')
        act_clear.triggered.connect(self.filter_clear)
        btn_clear = create_tool_button(self, act_clear, QStyle.SP_LineEditClearButton)
        toolbar.addWidget(btn_clear)

        act_search = QAction('Потърси', self)
        act_search.setToolTip('Извежда панел, чрез който може да се търси в съдържанието на имейлите')
        act_search.triggered.connect(self.open_search)
        btn_search = create_tool_button(self, act_search, QStyle.SP_MessageBoxQuestion)
        toolbar.addWidget(btn_search)

        self.navigator = MboxNavigator()
        self.messages = MessagesList()
        self.navigator.set_propagation_nid(self.messages.set_nid)

        splitter = QSplitter(self)
        splitter.addWidget(self.navigator)
        splitter.addWidget(self.messages)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 9)

        top = QWidget()
        top.setObjectName('topWidget')
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        top.setLayout(vbox)

        self.search = SearchWidget(self.navigator.load_tree_nodes)
        self.search.hide()

        vbox.addWidget(self.search)
        vbox.addWidget(splitter)

        self.setCentralWidget(top)
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
            self.navigator.last_selected_nid = None
            self.navigator.load_tree_nodes()

    def filter_only_colored(self):
        if mbox_wrapper.mbox is not None:
            found = mbox_wrapper.mbox.search_categories()
            found = found['nid'] if found is not None else None
            self.navigator.load_tree_nodes(found)

    def filter_clear(self):
        if mbox_wrapper.mbox is not None:
            mbox_wrapper.mbox.set_filter(None)
            self.navigator.load_tree_nodes()

    def closeEvent(self, event):
        self.messages.handle_close()
        super().closeEvent(event)

    def open_search(self):
        if self.search.isHidden():
            self.search.show()
        else:
            self.search.hide()


def exception_hook(_etype, value, trace):
    text = traceback.format_tb(trace)
    text.insert(0, '%s\n' % value)
    text = ''.join(text)
    print(text, file=sys.stderr)

    if QApplication.instance() is not None:
        dialog = QMessageBox()
        dialog.setStandardButtons(QMessageBox.Ignore | QMessageBox.Abort)
        dialog.setDefaultButton(QMessageBox.Ignore)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle('Грешка')
        dialog.setTextFormat(Qt.RichText)
        dialog.setText('<b>В програмата възникна непредвидена грешка.</b>')
        dialog.setInformativeText(str(value))
        dialog.setDetailedText(text)
        dialog.exec()
        if dialog.clickedButton() == QMessageBox.Abort:
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
