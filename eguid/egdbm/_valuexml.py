# -*- coding: utf-8 -*-
###############################################################################
# Name: _value.py                                                             #
# Purpose: Value field to do type coercion                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Xml Value Attribute

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['EgdValue',]

#-----------------------------------------------------------------------------#
# Imports
from dexml import fields

#-----------------------------------------------------------------------------#

class EgdValue(fields.Value):
    """Xml tag attribute value
    Handles type coercion to convert between xml and python object for
    generic value type handler.

    """
    def parse_value(self,val):
        try:
            val = eval(val)
        except Exception, msg:
            pass # assume its a string value
        return val

    def render_value(self,val):
        return repr(val)
