# -*- coding: utf-8 -*-
###############################################################################
# Name: _library.py                                                           #
# Purpose: Designer Library Object XML                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Designer Library Object Xml

XML to represent a control library for the designer.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['EgdLibrary', 'EgdControl']

#-----------------------------------------------------------------------------#
# Imports
import dexml
from dexml import fields

# Eguid imports
import _basexml

#-----------------------------------------------------------------------------#

class EgdLibrary(_basexml.EgdXml):
    """Designer Control Library Collection
    <library name='wx' version="2.8.11.0">
      <control name='Button'/>
      <control name='Choice'/>
    </library>
    """
    class meta:
        tagname = "library"
    name = fields.String(required=True)
    version = fields.String(required=False)
    controls = fields.List(fields.Model("control"), required=False)

class EgdControl(_basexml.EgdXml):
    """This class serializes the library description of a control
    <control name='Button' module='wx'/>
    """
    class meta:
        tagname = "control"
    name = fields.String(required=True)
    module = fields.String(required=True)
