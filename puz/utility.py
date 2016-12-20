#!/usr/bin/python3

from decimal import Decimal as _Decimal

def clean(val, quant=None):
    try:
        val = _Decimal(val)
    except:
        raise
    val = val.normalize()
    if quant:
        val = val.quantize(_Decimal(quant))
    return val

Decimal = lambda val,quant=None: clean(val,quant)

class Quantity():
    def __init__(self, val, units="mm"):
        q = unitreg.Quantity(val)
        if q.dimensionless:
            q2 = unitreg.Quantity("1 %s" % (units,))
            q._units = q2._units
        self.q = q

    def __lt__(self, other):
        if isinstance(other, Quantity):
            return self.mm < other.mm
        else:
            o = Decimal(other)
            s = Decimal(self.mm)
            return s < o

    def __eq__(self, other):
        if isinstance(other, Quantity):
            return self.mm == other.mm
        else:
            o = Decimal(other)
            s = Decimal(self.mm)
            return s == o

    def __hash__(self):
        return hash(self.q)

    def __str__(self):
        return str(self.q)

    def __abs__(self):
        mm = abs(self.mm)
        x = self.__class__.__new__(Quantity)
        x.__init__(val=mm, units="mm")
        return x

    @property
    def mm(self):
        m = self.q.to("mm").magnitude
        return Decimal(m, "10000000000.0000")

def frange(x, y, jump, quant=None):
    x = clean(x, quant=quant)
    y = clean(y, quant=quant)
    jump = clean(jump, quant=quant)
    if jump > 0:
        compare = lambda x,y: x <= y
    else:
        compare = lambda x,y: x >= y
    x = x - jump
    while compare(x + jump, y):
        x = x + jump
        yield float(clean(x, quant=quant))
    #tmpx = x + jump
    #if not compare(tmpx, y):
    #    yield float(clean(y, quant=quant))

__all__ = [
        "clean",
        "Decimal",
        "frange",
        ]

