#!/usr/bin/python3

from attr import attrs, attrib
from attr.validators import instance_of, optional, provides
import re

from .validators import *

import pdb

@attrs
class Page:
    width = attrib(validator=positive(number))
    height = attrib(validator=positive(number))

    margin_left = attrib(validator=number)
    margin_right = attrib(validator=number)

@attrs(slots=True)
class Column:
    anchor_to_top = attrib(default=False, validator=instance_of(bool))
    anchor_to_bottom = attrib(default=False, validator=instance_of(bool))

@attrs(slots=True)
class TallColumn(Column):
    def __init__(self):
        self.anchor_to_top = True
        self.anchor_to_bottom = True

@attrs(slots=True)
class TopColumn(Column):
    def __init__(self):
        self.anchor_to_top = True
        self.anchor_to_bottom = False

@attrs(slots=True)
class BottomColumn(Column):
    def __init__(self):
        self.anchor_to_top = False
        self.anchor_to_bottom = True

def cb(s):
    ret = []
    for c in s:
        if c == 'T':
            ret.append(TallColumn)
        elif c == 't':
            ret.append(TopColumn)
        elif c == 'b':
            ret.append(BottomColumn)
        else:
            raise ValueError('"%c" must be one of: T t b' % (c,))
    return tuple(ret)

@attrs
class Grid:
    quadrant = attrib(validator=onetofour)
    rows = attrib(default=13, validator=positive(instance_of(int)))
    cols = attrib(default=13, validator=positive(instance_of(int)))

    # line width in dots
    line_width = attrib(default=2, validator=positive(number))
    # size as pct of paper (inside margin box)
    size = attrib(default=60, validator=percentage)

@attrs
class Plan:
    clues_min = attrib(validator=number)
    clues_max = attrib(validator=positive(number))

    cols = attrib(validator=instance_of(tuple))

    grid_min = attrib(default=0.62, validator=percentage)
    grid_max = attrib(default=0.70, validator=percentage)

    font_min = attrib(default=9.1, validator=positive(number))
    font_max = attrib(default=12.0, validator=positive(number))

    font_name = attrib(default="Carlito", validator=instance_of(str))
    font_weight = attrib(default="Regular", validator=instance_of(str))

    margin_mult = attrib(default=1.0, validator=number)
    margin_add = attrib(default=0, validator=number)
    bottom_margin_add = attrib(default=0, validator=number)
    top_margin_add = attrib(default=0, validator=number)

    new_down_col = attrib(default=False, validator=instance_of(bool))

    grid_position = attrib(default=1, validator=onetofour)

    clue_letters_min = attrib(default=None, validator=optional(number))
    clue_letters_max = attrib(default=None,
				validator=optional(positive(number)))

    _tall_left_cols = attrib(default=0, validator=instance_of(int))
    _tall_right_cols = attrib(default=0, validator=instance_of(int))
    _top_left_cols = attrib(default=0, validator=instance_of(int))
    _top_right_cols = attrib(default=0, validator=instance_of(int))
    _bottom_left_cols = attrib(default=0, validator=instance_of(int))
    _bottom_right_cols = attrib(default=0, validator=instance_of(int))

class PuzzleParser:
    def __init__(self, puz):
        self.data = puz.data
        self.puz = puz
        self.pos = 0

    def read_string(self):
        l = len(self.data)
        if self.pos == l:
            return ''
        s = ''
        c = self.readc()
        while ord(c) is not 0 and self.pos < l:
            s += c
            c = self.readc()

        result = s
        ellipsis_char = 133
        result = result.replace(chr(ellipsis_char), '...')
        result = result.encode(encoding='iso_8859-1')
        return result

    def seek(self, pos):
        self.pos = pos
        return pos

    def readb(self):
        c = self.data[self.pos]
        self.pos += 1
        return c

    def readc(self):
        c = chr(self.readb())
        return "%c" % (c,)

    def process_section(self, code):
        if code == ['G', 'E', 'X', 'T']:
            count = ord(self.data[self.pos]) + 256 * ord(self.data[self.pos+1])
            self.pos += 2
            junk = self.data[self.pos:self.pos+1]
            self.pos += 2
            data = self.data[self.pos:self.pos+count]
            self.pos += count
            zero = self.data[self.pos]

            index = 0
            for y in range(self.puz.height):
                for x in range(self.puz.width):
                    if ord(data[index]) == 0x80:
                        self.puz.circles[x, y] = True
                    index += 1
        elif code == ['G', 'R', 'B', 'S']:
            count = ord(self.data[self.pos]) + 256 * ord(self.data[self.pos+1])
            self.pos += 2
            junk = self.data[self.index:self.index+1]
            self.pos += 2
            data = self.data[self.pos:self.pos+count]
            self.pos += count
            zero = self.data[self.pos]
            self.pos += 1

            index = 0
            for y in range(self.puz.height):
                for x in range(self.puz.width):
                    self.puz.rebus[x, y] = ord(data[index])
                    index += 1
        elif code == ['R', 'T', 'B', 'L']:
            self.pos += 7
        elif code == ['W', 'E', 'N', 'S']:
            self.pos += 2

    def parse(self):
        def massage(s):
            # skips unprintable characters
            snew = ''
            for c in s:
                if c >= ord(' ') and c <= ord('~'):
                    snew += '%c' % (c,)

            return snew.lstrip().rstrip()

        self.seek(0x2c)
        self.puz.width = width = self.readb()
        self.puz.height = height = self.readb()

        self.puz.answers = {}
        self.seek(0x34)
        for y in range(height):
            for x in range(width):
                self.puz.answers[x, y] = self.readc()

        self.puz.responses = {}
        for y in range(height):
            for x in range(width):
                c = self.readc()
                if c == '-':
                    c = ''
                self.puz.responses[x, y] = c

        pub = ""
        title = massage(self.read_string())
        r = re.compile(r'(.*, [SMTWFabcdefghijklmnopqrstuvwxyz]+, [JFMASONDabcdefghijklmnopqrstuvwxyz]+ [0-9]+, [0-9]{4}) (.*)')
        m = r.match(title)
        try:
            g = m.groups()
            if len(g) == 2:
                pub = g[0]
                title = g[1]
        except:
            pass

        self.puz.pub = massage(pub.encode(encoding='iso_8859-1'))
        self.puz.title = massage(title.encode(encoding='iso_8859-1'))
        self.puz.author = massage(self.read_string())
        self.puz.copyright = massage(self.read_string())

        self.puz.clues = []
        clue = self.read_string()
        while clue:
            self.puz.clues.append(clue)
            clue = self.read_string()

        limit = len(self.data)
        while limit > self.pos:
            code = self.data[self.pos:self.pos+4]
            self.pos += 4
            self.process_section(code)

@attrs
class Puzzle:
    data = attrib(repr=False)

    pub = attrib(default="", validator=instance_of(str))
    title = attrib(default="", validator=instance_of(str))
    author = attrib(default="", validator=instance_of(str))
    copyright = attrib(default="", validator=instance_of(str))

    across_clues = attrib(default=[], validator=instance_of(list), repr=False)
    down_clues = attrib(default=[], validator=instance_of(list), repr=False)
    across_answers = attrib(default=[], validator=instance_of(list), repr=False)
    down_answers = attrib(default=[], validator=instance_of(list), repr=False)

    clues = attrib(default=[], validator=instance_of(list), repr=False)
    answers = attrib(default=[], validator=instance_of(list), repr=False)
    responses = attrib(default=[], validator=instance_of(list), repr=False)
    rebus = attrib(default={}, validator=instance_of(dict), repr=False)
    circles = attrib(default={}, validator=instance_of(dict), repr=False)

    grid = attrib(init=False, validator=optional(instance_of(Grid)), repr=False)

    def parse(self):
        p = PuzzleParser(self)
        p.parse()

class PuzzlePlanner:
    plans = [
        Plan(0, 50, cols=cb("Tb"), new_down_col=True, grid_max=1.2),
        Plan(50, 70, cols=cb("Tbb"), new_down_col=True, grid_max=1.2),
        Plan(70, 85, cols=cb("Tbb"), grid_max=1.2, font_max=13),
        Plan(85, 95, cols=cb("Tbb"), grid_max=1.2),
        Plan(95, 110, cols=cb("Tbbb")),
        Plan(110, 130, cols=cb("Tbbb"), margin_add=-15, grid_min=0.60, font_min=8.0),
        Plan(130, 138, cols=cb("Tbbb"), margin_add=-15, grid_min=0.60, font_min=8.0),
        Plan(138, 140, cols=cb("TTbb"), margin_add=-15, grid_min=0.66),
        Plan(140, 141, cols=cb("Tb"), margin_add=-30, grid_min=0.5, font_min=7.0, bottom_margin_add=-15),
        Plan(141, 145, cols=cb("TTbbb"), margin_add=-30, grid_min=0.625, font_min=8.2, bottom_margin_add=-15),
            ]

__all__ = ["Page", "Column", "TallColumn", "TopColumn", "BottomColumn", "Grid", "Plan", "Puzzle", "PuzzlePlanner"]
