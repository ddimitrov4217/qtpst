# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging
from collections import namedtuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyle, QTreeWidget, QTreeWidgetItem
from readms.readpst import PropertyContext

from qtpst import mbox_wrapper

MboxNode = namedtuple('MboxNode', ['name', 'mcnt', 'tcnt', 'nid', 'children'])
log = logging.getLogger(__name__)


class MboxNavigator(QTreeWidget):
    def __init__(self, with_empty=False):
        super().__init__()
        self.with_empty = with_empty
        self.initUI()
        self.propagate_nid = None
        self.data = None
        self.last_selected_nid = None

    def initUI(self):
        self.setColumnCount(4)
        for col, width in enumerate((220, 40, 40, 5)):
            self.setColumnWidth(col, width)
        self.setHeaderLabels(['Папка', 'Съобщения', 'Директни', ''])
        self.currentItemChanged.connect(self.handle_item_clicked)
        self.setObjectName('navigator')

    def load_tree_nodes(self, select_nid=None):
        items = []
        self.data = {}
        # https://www.pythonguis.com/faq/built-in-qicons-pyqt/
        icon = self.style().standardIcon(QStyle.SP_DirIcon)

        def get_total_messages(node):
            result = node.mcnt
            for cx in node.children:
                result += get_total_messages(cx)
            return result

        def add_node(node, parent=None):
            tcnt = get_total_messages(node)
            if not self.with_empty and tcnt == 0:
                return

            item = QTreeWidgetItem()
            item.setText(0, node.name)
            item.setText(1, f"{tcnt if tcnt > 0 else ''}")
            item.setText(2, f"{node.mcnt if node.mcnt > 0 else ''}")
            item.setTextAlignment(1, Qt.AlignRight)
            item.setTextAlignment(2, Qt.AlignRight)
            item.setIcon(0, icon)
            self.data[id(item)] = node

            if select_nid is not None and node.nid['nid'] == select_nid:
                selected['filter_found'] = item

            if self.last_selected_nid is not None and node.nid['nid'] == self.last_selected_nid:
                selected['last_selected'] = item

            if parent is not None:
                parent.addChild(item)
            else:
                items.append(item)
            for node_ in node.children:
                add_node(node_, item)

        log.debug(select_nid)
        selected = {}

        for node_ in get_pst_folder_hierarchy():
            add_node(node_)

        self.clear()
        self.insertTopLevelItems(0, items)
        self.expandAll()

        selected_item = None
        for select_priority in ('last_selected', 'filter_found'):
            if select_priority in selected:
                selected_item = selected[select_priority]
                break
        if selected_item is None and items:
            selected_item = items[0]

        if selected_item is not None:
            selected_item.setSelected(True)
            self.refresh_messages(self.data.get(id(selected_item)).nid['nid'])

    def set_propagation_nid(self, func):
        self.propagate_nid = func

    def handle_item_clicked(self, current, _previous):
        node = self.data.get(id(current), None)
        if node is not None:
            log.debug('%d: %s', node.nid['nid'], node.name)
            self.last_selected_nid = node.nid['nid']
            self.refresh_messages(node.nid['nid'])

    def refresh_messages(self, nid):
        if self.propagate_nid is not None:
            self.propagate_nid(nid)


def get_pst_folder_hierarchy():
    nodes_list = []  # MboxNode
    nodes_dict = {}
    ndb = mbox_wrapper.mbox.get_mbox()

    for nx in ndb._nbt:
        if (nx["typeCode"] != "NORMAL_FOLDER" or nx["nid"] == nx["nidParent"]):
            continue
        pc = PropertyContext(ndb, nx['nid'])
        mcnt = mbox_wrapper.mbox.count_messages(nx['nid'])
        name = pc.get_value_safe('DisplayName')
        node = MboxNode(name=name, mcnt=mcnt, tcnt=0, nid=nx, children=[])
        nodes_dict[nx['nid']] = node

        parent = nodes_dict.get(nx['nidParent'], None)
        if parent is not None:
            parent.children.append(node)
        else:
            nodes_list.append(node)

    return nodes_list
