#!/usr/bin/python3

import pdb
import sys

from attr import attrs, attrib
from attr.validators import instance_of, optional, provides
from .validators import *
from .cairo import Point, Line
from .utility import *

@attrs
class Page:
    real_width = attrib(validator=positive(number))
    real_height = attrib(validator=positive(number))

    left_margin = attrib(validator=positive(number))
    right_margin = attrib(validator=positive(number))
    top_margin = attrib(validator=positive(number))
    bottom_margin = attrib(validator=positive(number))

    @property
    def real_area(self):
        return self.real_width * self.real_height

    @property
    def width(self):
        return self.real_width - self.left_margin - self.right_margin

    @property
    def height(self):
        return self.real_height - self.top_margin - self.bottom_margin

    @property
    def area(self):
        return self.width * self.height

    @property
    def top_edge(self):
        return 0

    @property
    def bottom_edge(self):
        return self.height

    @property
    def left_edge(self):
        return 0

    @property
    def right_edge(self):
        return self.width

@attrs(repr=False)
class OffsetBox:
    xy = attrib(validator=instance_of(Point))
    width = attrib(validator=positive(number))
    height = attrib(validator=positive(number))

    parent = attrib(default=None, validator=instance_of(OffsetBox))

    def __repr__(self):
        if self.parent:
            xy = parent.adjust(self.xy)
            width = parent.limit_x(self.xy.x + self.width)
            height = parent.limit_y(self.xy.y + self.height)
            return "OffsetBox(xy=%s,width=%s,height=%s)" % (xy, width, height))
        return "OffsetBox(xy=%s,width=%s,height=%s)" % (self.xy, self.width,
                self.height))

    def adjust

@attrs
class Grid:
    page = attrib(validator=instance_of(Page))

    # quadrant = attrib(validator=instance_of(Quadrant))
    rows = attrib(default=15, validator=positive(instance_of(int)))
    cols = attrib(default=15, validator=positive(instance_of(int)))

    # line width in dots
    line_width = attrib(default=float(18/72), validator=positive(number))

    debug = attrib(default=False, validator=instance_of(bool))

    @property
    def box_size(self):
        return self.page.plan.box_size

    @property
    def width(self):
        lines = (self.cols + 1) * self.line_width
        lines = 0
        spaces = self.box_size * self.cols
        print("spaces: %s lines: %s" % (spaces,lines), file=sys.stderr)
        return spaces + lines

    @property
    def height(self):
        lines = (self.rows + 1) * self.line_width
        lines = 0
        spaces = self.box_size * self.rows
        print("spaces: %s lines: %s" % (spaces,lines), file=sys.stderr)
        return spaces + lines

    @property
    def verticals(self):
        top = self.page.top_edge
        bottom = self.page.top_edge + self.height - self.line_width
        for x in frange(self.page.right_edge - self.width,
                        self.page.right_edge,
                        self.box_size):

            start = Point(x, top)
            end = Point(x, bottom)
            print("INFO: vertical line from %s to %s" % (start, end))
            yield Line(start, end)

    @property
    def horizontals(self):
        left = self.page.right_edge - self.width + self.line_width
        right = self.page.right_edge
        for y in frange(self.page.top_edge,
                        self.page.top_edge + self.height,
                        self.box_size):
            start = Point(left, y)
            end = Point(right, y)
            print("INFO: horizontal line from %s to %s" % (start, end))
            yield Line(start, end)

    def draw(self):
        print("INFO: rows: %s columns: %s" % (self.rows, self.cols),
                file=sys.stderr)
        print("INFO: width: %s height: %s" % (self.width,
            self.height), file=sys.stderr)
        print("INFO: line width: %s" % (self.line_width), file=sys.stderr)

        ctx = self.page.ctx

        ctx.set_source_rgb(0, 0, 0)

        ctx.set_line_width(self.line_width)
        for vertical in self.verticals:
            ctx.move_to(vertical.start)
            ctx.line_to(vertical.end)
            ctx.stroke()

        for horizontal in self.horizontals:
            ctx.move_to(horizontal.start)
            ctx.line_to(horizontal.end)
            ctx.stroke()

__all__ = ["Page", "Grid"]
