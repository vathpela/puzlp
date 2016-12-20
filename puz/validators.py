#!/usr/bin/python3

import attr
from attr import attrs, attrib
from attr.validators import instance_of, optional, provides

from .utility import *

def number(instance, attribute, value):
    if not isinstance(value, float) and not isinstance(value, int):
        raise TypeError('"%s" must be a number' % (attribute,))

@attr._make.attributes(repr=False, slots=True)
class _PositiveValidator:
    validator = attr._make.attr()

    def __call__(self, inst, attr, value):
        if value < 0:
            raise ValueError('"%s" must be greater than 0' % (attr,))
        return self.validator(inst, attr, value)

    def __repr__(self):
        return (
            "<positive validator for {type}>"
            .format(type=repr(self.validator))
        )

def positive(validator):
    """
    A validator that requires an attribute to be non-negative.

    :param validator: A validator that is used for non-negative values.
    """
    return _PositiveValidator(validator)

def percentage(instance, attribute, value):
    positive(number(instance, attribute, value))
    if value > 100:
        raise ValueError('"%s" cannot be greater than 100' % (attribute,))

__all__ = ["number", "positive", "percentage"]
