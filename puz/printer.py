#!/usr/bin/python3

import os
import cups
import pdb
import pprint

from attr import attrs, attrib
from attr.validators import instance_of, optional, provides

from .validators import *

@attrs
class Printer:
    jobid = attrib()
    options = attrib()
    ppd = attrib(default=os.environ['PPD'])
    queue = attrib(default=os.environ['PRINTER'])
    cachedir = attrib(default=os.environ['CUPS_CACHEDIR'])
    datadir = attrib(default=os.environ['CUPS_DATADIR'])
    serverroot = attrib(default=os.environ['CUPS_SERVERROOT'])
    device_uri = attrib(default=os.environ['DEVICE_URI'])

    def connect(self, log):
        print("queue: %s" % (self.queue,), file=log)
        print("jobid: %s" % (self.jobid,), file=log)
        print("options: %s" % (self.options,), file=log)
        self.jobid = int(self.jobid)
        def cb(*args, **kwargs):
            print("cb args: %s" % (args,), file=log)
            print("cb kwargs: %s" % (kwargs,), file=log)
        self.conn = cups.Connection()
        printers = self.conn.getPrinters()
        options = {}
        for option in self.options.split(' '):
            if '=' in option:
                k,v = option.split('=')
                options[k] = v
            else:
                options[option] = ""
        self.options = options
        self.printer = printers[self.queue]
        self.pattrs = self.conn.getPrinterAttributes(self.queue)
        self.jobattrs = self.conn.getJobAttributes(self.jobid)
        pprint.pprint(self.jobattrs, stream=log)

    @property
    def media(self):
        return int(self.options['media'])

    @property
    def media_name(self):
        if 'media' in self.options:
            return self.pattrs['media-supported'][self.media]

    @property
    def top_margin(self):
        return self.pattrs['media-top-margin-supported'][0]

    @property
    def bottom_margin(self):
        return self.pattrs['media-bottom-margin-supported'][0]

    @property
    def left_margin(self):
        return self.pattrs['media-left-margin-supported'][0]

    @property
    def right_margin(self):
        return self.pattrs['media-right-margin-supported'][0]

    @property
    def dpi(self):
        return self.pattrs['printer-resolution-default'][0]

    @property
    def width(self):
        return self.dpi * 8.5

    @property
    def height(self):
        return self.dpi * 11

    @property
    def top_bound(self):
        return self.top_margin

    @property
    def bottom_bound(self):
        return self.height - self.bottom_margin

    @property
    def left_bound(self):
        return self.left_margin

    @property
    def right_bound(self):
        return self.width - self.right_margin


__all__ = ["Printer"]
