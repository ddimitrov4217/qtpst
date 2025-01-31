# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import sys
from collections import namedtuple
from os import getcwd, path

from readms.pstwrap import global_env, mbox_wrapper
from readms.readpst import PropertyContext

MboxNode = namedtuple('MboxNode', ['name', 'mcnt', 'tcnt', 'nid', 'children'])


def init_mbox():
    config_file = path.abspath(path.join(getcwd(), "appconfig.ini"))
    global_env.setup_env(config_file)
    mbox_wrapper.init_mbox_wrapper(global_env.config)


def read_pst(pst_file):
    mbox_wrapper.close_mbox()
    mbox_wrapper.open_mbox(pst_file)


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


# за изпозлване при разучаване на PyQt
init_mbox()
read_pst(sys.argv[1] if len(sys.argv) > 1 else '2020.pst')
