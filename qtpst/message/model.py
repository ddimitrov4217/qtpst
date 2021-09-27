# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging
from collections import namedtuple
from readms.readpst import PropertyValue, PropertyContext
from readms.readmsg import PropertiesStream
from readms.readmsg import Message as OleMessage, Attachment as OleAttachment

from .. import mbox_wrapper

log = logging.getLogger(__name__)

AttributeValue = namedtuple('AttributeValue', ['code', 'vtype', 'vsize', 'value'])


class AttributesContainer:
    def __init__(self):
        self.name = id(self)
        self.properties = []  # AttributeValue
        self.dict = {}

    def load_dict(self):
        ino = 1
        for attv in self.properties:
            pkey = attv.code
            if pkey in self.dict:
                pkey = '%s.%d' % (pkey, ino)
                ino += 1
            self.dict[pkey] = attv

    def dump_hier(self):
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

        dump_entry(self)


class Message(AttributesContainer):
    def __init__(self):
        super().__init__()
        self.attachments = []
        self.recipients = []


class Recipient(AttributesContainer):
    pass


class Attachment(AttributesContainer):
    def __init__(self):
        super().__init__()
        self.message = None


class MessageNid(Message):
    def __init__(self, nid):
        super().__init__()

        self.pc = PropertyContext(mbox_wrapper.mbox.get_mbox(), nid)
        for pname in self.pc._propx:
            ptag = self.pc._propx[pname]
            pt = self.pc._props[ptag]['propType']
            pv = PropertyValue(pt, self.pc.get_buffer(ptag))
            attv = create_att_value(pname, pv)
            self.properties.append(attv)
        self.load_dict()

        def att_str(code, value):
            vsize = len(value) if value is not None else 0
            return AttributeValue(code=code, vtype='String', vsize=vsize, value=value)

        def att_int(code, value):
            return AttributeValue(code=code, vtype='Integer', vsize=8, value=value)

        def att_boo(code, value):
            return AttributeValue(code=code, vtype='Boolean', vsize=8, value=value)

        for ano, att_ in enumerate(mbox_wrapper.mbox.list_attachments(nid)):
            _nid, anid, name, size, _mimet, _mime, cid = att_
            data_mime, data_name, data = mbox_wrapper.mbox.get_attachment(nid, anid)

            att = Attachment()
            self.attachments.append(att)
            att.properties.append(AttributeValue(
                code='AttachDataObject', vtype='Binary', vsize=size,
                value=PropertyValue.BinaryValue(data)))

            att.properties.append(att_int('AttachNumber', ano))
            att.properties.append(att_str('AttachFilename', name))
            att.properties.append(att_str('AttachLongFilename', data_name))
            att.properties.append(att_str('DisplayName', data_name))
            att.properties.append(att_str('AttachMimeTag', data_mime))
            att.properties.append(att_str('AttachContentId', cid))
            if cid is not None and cid.startswith('image'):
                att.properties.append(att_boo('AttachmentHidden', True))

            # TODO AttacheMethod, AttachmenHidden ObjectType
            # TODO да се различават приложените съобщения и да се зареждат

            att.load_dict()


class MessageMsg(Message):
    def __init__(self, msgfile):
        super().__init__()
        with PropertiesStream(msgfile) as ole:
            msgole = OleMessage(ole, ole.root)
            self.copy(msgole, self)
        self.load_dict()

    def copy(self, src, dst):
        copy_ole_properties(src.properties, dst.properties)
        dst.load_dict()

        if isinstance(src, OleMessage):
            for rcp_src in src.recipients:
                rcp_dst = Recipient()
                self.copy(rcp_src, rcp_dst)
                dst.recipients.append(rcp_dst)
                dst.load_dict()

            for att_src in src.attachments:
                att_dst = Attachment()
                self.copy(att_src, att_dst)
                dst.attachments.append(att_dst)
                dst.load_dict()

        if isinstance(src, OleAttachment):
            if src.message is not None:
                dst.message = Message()
                self.copy(src.message, dst.message)
                dst.load_dict()


def create_att_value(code, pv):
    vtype, _, _ = pv.pt_desc
    vsize = len(pv._buf)
    value = pv.get_value()
    if vtype == 'Binary':
        value = PropertyValue.BinaryValue(value.data)
    return AttributeValue(code=code, vtype=vtype, vsize=vsize, value=value)


def copy_ole_properties(src, dst):
    for atts in src:
        attv = create_att_value(atts.prop['propCode'], atts.value)
        dst.append(attv)
