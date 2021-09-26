# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

import logging

from readms.readpst import PropertyValue, PropertyContext
from readms.readmsg import Property

from .. import mbox_wrapper

log = logging.getLogger(__name__)

# TODO Да се нарави с наистина общи (наследени) класове със readms.readmsg


def read_nid(nid):
    return Message(nid)


class AttributesContainer:
    def __init__(self):
        self.name = id(self)
        self.properties = []
        self.dict = {}

    def load_dict(self):
        # XXX Това е копирано едно към едно
        ino = 1
        for px in self.properties:
            pkey = px.prop['propCode']
            if pkey in self.dict:
                pkey = '%s.%d' % (pkey, ino)
                ino += 1
            self.dict[pkey] = px


class Message(AttributesContainer):
    def __init__(self, nid):
        super().__init__()
        self.attachments = []
        self.recipients = []
        self.pc = PropertyContext(mbox_wrapper.mbox.get_mbox(), nid)

        for pname in self.pc._propx:
            ptag = self.pc._propx[pname]
            pt = self.pc._props[ptag]['propType']
            pv = PropertyValue(pt, self.pc.get_buffer(ptag))
            pv = Property(value=pv, prop=self.pc._props[ptag])
            self.properties.append(pv)

        self.load_dict()


class Recipient(AttributesContainer):
    def __init__(self):
        super().__init__()


class Attachment(AttributesContainer):
    def __init__(self):
        super().__init__()
        self.message = None
