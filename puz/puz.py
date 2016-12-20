#!/usr/bin/python3

from attr import attrs, attrib
from attr.validators import instance_of, optional, provides
import re

import pdb

from .validators import *
from .drawing import *

@attrs(slots=True, init=False)
class Quadrant:
    quadrant = attrib(init=False, validator=instance_of(int))

    def __init__(self, quadrant):
        if quadrant < 1 or quadrant > 4:
            raise ValueError('quadrant must be 1 through 4')
        self.quadrant = quadrant

@attrs(slots=True)
class LetterBox:
    x = attrib(validator=positive(instance_of(int)))
    y = attrib(validator=positive(instance_of(int)))
    circle = attrib(default=False, validator=instance_of(bool))

@attrs(slots=True)
class Column:
    anchor_to_top = attrib(default=False, validator=instance_of(bool))
    anchor_to_bottom = attrib(default=False, validator=instance_of(bool))
    clues = attrib(default=[])

@attrs(slots=True)
class TallColumn(Column):
    anchor_to_top = True
    anchor_to_bottom = True

@attrs(slots=True)
class TopColumn(Column):
    anchor_to_top = True
    anchor_to_bottom = False

@attrs(slots=True)
class BottomColumn(Column):
    anchor_to_top = False
    anchor_to_bottom = True

@attrs(slots=True)
class Clue:
    startxy = attrib(validator=instance_of(LetterBox))
    endxy = attrib(validator=instance_of(LetterBox))
    number = attrib(validator=instance_of(int))
    text = attrib(validator=instance_of(str))

    @property
    def across(self):
        if startxy.x == endxy.x:
            return True
        return False

    @property
    def down(self):
        return not self.across

    def __len__(self):
        return len(self.text)

    def size(self, font, weight):
        pass


@attrs
class PuzzleParser:
    puz = attrib()
    data = attrib(repr=0)

    _pos = attrib(default=0, repr=0)

    @property
    def pos(self):
        return self._pos

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

    def seek(self, pos, whence=0):
        if whence==1:
            self._pos += pos
        else:
            self._pos = pos
        return pos

    def readb(self):
        c = self.data[self.pos]
        self._pos += 1
        return c

    def readc(self):
        c = chr(self.readb())
        return "%c" % (c,)

    def process_section(self, code):
        if code == ['G', 'E', 'X', 'T']:
            count = ord(self.data[self.pos]) + 256 * ord(self.data[self.pos+1])
            self._pos += 2
            junk = self.data[self.pos:self.pos+1]
            self._pos += 2
            data = self.data[self.pos:self.pos+count]
            self._pos += count
            zero = self.data[self.pos]
            self._pos += 1

            index = 0
            for y in range(self.puz.height):
                for x in range(self.puz.width):
                    if ord(data[index]) == 0x80:
                        self.puz.circles[x, y] = True
                    index += 1
        elif code == ['G', 'R', 'B', 'S']:
            count = ord(self.data[self.pos]) + 256 * ord(self.data[self.pos+1])
            self._pos += 2
            junk = self.data[self.index:self.index+1]
            self._pos += 2
            data = self.data[self.pos:self.pos+count]
            self._pos += count
            zero = self.data[self.pos]
            self._pos += 1

            index = 0
            for y in range(self.puz.height):
                for x in range(self.puz.width):
                    self.puz.rebus[x, y] = ord(data[index])
                    index += 1
        elif code == ['R', 'T', 'B', 'L']:
            self._pos += 7
        elif code == ['W', 'E', 'N', 'S']:
            self._pos += 2

    def is_black(self, x, y):
        return self.puz.responses.get((x, y), '.') == '.'

    def is_circle(self, x, y):
        return self.puz.circles.has_key((x, y))

    def parse(self):
        def massage(s):
            # skips unprintable characters
            snew = ''
            for c in s:
                if c >= ord(' ') and c <= ord('~'):
                    snew += '%c' % (c,)

            return snew.lstrip().rstrip()

        self.across_clues = {}
        self.down_clues = {}
        self.across_map = {}
        self.down_map = {}
        self.number_map = {}
        self.number_rev_map = {}
        self.mode_maps = [self.across_map, self.down_map]
        self.mode_clues = [self.across_clues, self.down_clues]
        self.is_across = {}
        self.is_down = {}
        self.circles = {}
        self.rebus = {}
        self.clues = []

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

        clue = self.read_string()
        while clue:
            self.clues.append(clue)
            clue = self.read_string()

        limit = len(self.data)
        while limit > self.pos:
            code = self.data[self.pos:self.pos+4]
            self._pos += 4
            self.process_section(code)

        number = 1
        for y in range(height):
            for x in range(width):
                is_fresh_x = self.is_black(x-1, y)
                is_fresh_y = self.is_black(x, y-1)

                if not self.is_black(x, y):
                    if is_fresh_x:
                        self.across_map[x, y] = number
                        if self.is_black(x+1, y):
                            self.across_clues[number] = ''
                            is_fresh_x = False
                        else:
                            text = self.clues.pop(0).decode("iso_8859-1")
                            start = LetterBox(x, y)
                            end = LetterBox(x+len(text), y)
                            clue = Clue(start, end, number, text)
                            self.across_clues[number] = clue
                    else:
                        self.across_map[x, y] = self.across_map[x-1, y]
                    if is_fresh_y:
                        self.down_map[x, y] = number
                        if self.is_black(x, y+1): # see April 30, 2006 puzzle
                            self.down_clues[number] = ''
                            is_fresh_y = False
                        else:
                            text = self.clues.pop(0).decode("iso_8859-1")
                            start = LetterBox(x, y)
                            end = LetterBox(x, y+len(text))
                            clue = Clue(start, end, number, text)
                            self.down_clues[number] = clue
                    else:
                        self.down_map[x, y] = self.down_map[x, y-1]

                    if is_fresh_x or is_fresh_y:
                        self.is_across[number] = is_fresh_x
                        self.is_down[number] = is_fresh_y
                        self.number_map[number] = (x, y)
                        self.number_rev_map[x, y] = number
                        number += 1
                else:
                    self.across_map[x, y] = 0
                    self.down_map[x, y] = 0
        self.max_number = number-1

        self.puz.across_clues = self.across_clues
        self.puz.down_clues = self.down_clues
        self.puz.across_map = self.across_map
        self.puz.down_map = self.down_map

        self.puz.number_map = self.number_map
        self.puz.number_rev_map = self.number_rev_map
        self.puz.mode_maps = self.mode_maps
        self.puz.mode_clues = self.mode_clues

        self.puz.circles = self.circles

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
        p = PuzzleParser(self, self.data)
        p.parse()

    @property
    def clues(self):
        return len(self.down_clues) + len(self.across_clues)

__all__ = [
        "Grid", "Puzzle", "LetterBox", "Clue",
        "Column", "TallColumn", "TopColumn", "BottomColumn",
        "Quadrant",
        ]
