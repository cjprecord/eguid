# -*- coding: utf-8 -*-
###############################################################################
# Name: _project.py                                                           #
# Purpose: Project Xml Representation                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['EgdProject', 'EgdVersion']

#-----------------------------------------------------------------------------#
# Imports
import dexml
from dexml import fields

# Eguid imports
import _basexml
import _objectxml

#-----------------------------------------------------------------------------#

class EgdVersion(_basexml.EgdXml):
    """Xml File Version Tag
    <version major='1' minor='0'/>

    """
    class meta:
        tagname = "version"
    major = fields.Integer(required=True)
    minor = fields.Integer(required=True)

class EgdProject(_basexml.EgdXml):
    """Eguid Project Xml Format
    <EgdProject name="MyProject">
      <version major='1' minor='0'/>
      <object name='Frame' module='wx'>
         <property name='Size' value='(100,100)'/>
      </object>
    </EgdProject>
    """
    name = fields.String()
    version = fields.Model(EgdVersion, required=True)
    objects = fields.List(_objectxml.EgdObject, required=False)

#-----------------------------------------------------------------------------#
