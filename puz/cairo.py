#!/usr/bin/python3

import pdb

from collections import *

from attr import attrs, attrib
from attr.validators import instance_of, optional, provides
from .validators import *
from .utility import *

import cairo

FONT_SLANT_NORMAL = cairo.FONT_SLANT_NORMAL
FONT_WEIGHT_NORMAL = cairo.FONT_WEIGHT_NORMAL

@attrs(repr=False)
class Point:
    _x = attrib(validator=number)
    _y = attrib(validator=number)

    @property
    def x(self):
        return Decimal(self._x).normalize().quantize(Decimal(".00"))

    @property
    def y(self):
        return Decimal(self._y).normalize().quantize(Decimal(".00"))

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)

@attrs
class Line:
    start = attrib(validator=instance_of(Point))
    end = attrib(validator=instance_of(Point))

FontExtent = namedtuple("FontExtent", [
    "ascent",
    "descent",
    "height",
    "max_x_advance",
    "max_y_advance"])

TextExtent = namedtuple("TextExtent", [
    "x_bearing",
    "y_bearing",
    "width",
    "height",
    "x_advance",
    "y_advance"])

@attrs(init=False)
class PDFSurface:
    filename = attrib(validator=optional(instance_of(str)))
    width = attrib(validator=positive(number))
    height = attrib(validator=positive(number))

    _surface = attrib(validator=instance_of(cairo.PDFSurface))

    def __init__(self, filename, width=612, height=792):
        self.filename = filename
        self.width = width
        self.height = height

        self._surface = cairo.PDFSurface(filename, width, height)

    def set_device_offset(self, x, y):
        self._surface.set_device_offset(x, y)

@attrs(init=False)
class Context:
    surface = attrib(validator=instance_of(PDFSurface))

    _font_face = attrib(validator=optional(instance_of(str)))
    _font_slant = attrib(validator=optional(instance_of(int)))
    _font_weight = attrib(validator=optional(instance_of(int)))
    _font_size = attrib(validator=optional(number))

    _line_width = attrib(validator=optional(number))

    _x = attrib(validator=instance_of(int))
    _y = attrib(validator=instance_of(int))

    _ctx = attrib(validator=instance_of(cairo.Context))

    def __init__(self, surface):
        self.surface = surface
        self._ctx = cairo.Context(surface._surface)

        self._font_face = None
        self._font_slant = None
        self._font_weight = None
        self._font_size = None

        self._line_width = 1

        self.point = Point(0, 0)

    def move_to(self, point):
        self._ctx.move_to(point.x, point.y)
        self.location = point

    def line_to(self, point):
        self._ctx.line_to(point.x, point.y)
        self.location = point

    def rectangle(self, topleft, width, height):
        self._ctx.rectangle(topleft.x, topleft.y, width, height)

    def select_font_face(self, face, slant, weight):
        self._ctx.select_font_face(face, slant, weight)
        self._font_face = face
        self._font_slant = slant
        self._font_weight = weight

    def set_font_size(self, size):
        self._ctx.set_font_size(size)
        self._font_size = size

    def set_line_width(self, width):
        self._ctx.set_line_width(width)
        self._line_width = width

    def set_source_rgb(self, r, g, b):
        self._ctx.set_source_rgb(r, g, b)

    def show_text(self, text):
        self._ctx.show_text(text)

    def stroke(self):
        self._ctx.stroke()

    def get_scaled_font(self):
        return ScaledFont(self)

    def get_font_face(self):
        return self._ctx.get_font_face()


@attrs(init=False)
class ScaledFont:
    _sf = attrib(validator=instance_of(cairo.ScaledFont))
    _ctx = attrib(validator=instance_of(Context))

    def __init__(self, ctx):
        self._ctx = ctx
        self.sf = ctx._ctx.get_scaled_font()

    def text_extents(self, text):
        te = self.sf.text_extents(text)
        return TextExtent(*te)

__all__ = [
        "FONT_SLANT_NORMAL", "FONT_WEIGHT_NORMAL",
        "Point", "Line",
        "FontExtent", "TextExtent",
        "PDFSurface", "Context",
        ]
