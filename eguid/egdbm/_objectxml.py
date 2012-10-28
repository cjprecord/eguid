# -*- coding: utf-8 -*-
###############################################################################
# Name: _project.py                                                           #
# Purpose: Designer Object Xml                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Designer Object Xml

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['EgdObject', 'EgdProperty']

#-----------------------------------------------------------------------------#
# Imports
import dexml
from dexml import fields

# Eguid imports
import _basexml
import _valuexml

#-----------------------------------------------------------------------------#

class EgdProperty(_basexml.EgdXml):
    """Designer Control Property
    <property name='Size' value='(-1,-1)'/>
    """
    class meta:
        tagname = "property"
    name = fields.String(required=True)
    value = _valuexml.EgdValue(default=None, required=True)

class EgdObject(_basexml.EgdXml):
    """Designer Control Object
    <object name='Frame' module='wx'>
       <property name='Size' value='(100,100)'/>
       <object name='Panel' module='wx'>
           <object name='Button' module='wx'>
               <property name='Label' value='Push Me'/>
           </object>
       </object>
    </object>

    """
    class meta:
        tagname = "object"
    name = fields.String(required=True)
    module = fields.String(required=True)
    properties = fields.List(fields.Model(EgdProperty), required=False)
    objects = fields.List(fields.Model("object"), required=False)
