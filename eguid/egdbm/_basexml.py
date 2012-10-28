# -*- coding: utf-8 -*-
###############################################################################
# Name: _basexml.py                                                           #
# Purpose: XML Base Class                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['EgdXml',]

#-----------------------------------------------------------------------------#
# Imports
import types
from xml.dom import minidom

import dexml

#-----------------------------------------------------------------------------#

class EgdXml(dexml.Model):
    """XML base class"""
    def __init__(self, **kwds):
        super(EgdXml, self).__init__(**kwds)

    def getPrettyXml(self):
        """Get a nicely formatted version of the rendered xml string
        @return: string

        """
        txt = self.render()
        txt = minidom.parseString(txt).toprettyxml()
        txt = txt.replace('\t', '   ') # DeTabify
        return txt

    def getXml(self):
        """Get the XML string for this object
        @return: string

        """
        return self.render()

    def write(self, path):
        """Write the xml to a file
        @param path: string
        @return: success (bool)

        """
        suceeded = True
        try:
            xmlstr = self.getPrettyXml()
            if isinstance(xmlstr, types.UnicodeType):
                xmlstr = xmlstr.encode('utf-8')
            handle = open(path, 'wb')
            handle.write(xmlstr)
            handle.close()
        except (IOError, OSError, UnicodeEncodeError):
            suceeded = False
        return suceeded

    @classmethod
    def load(cls, path):
        """Load this object from a file
        @return: instance

        """
        instance = None
        try:
            handle = open(path, 'rb')
            xmlstr = handle.read()
            handle.close()
            instance = cls.parse(xmlstr)
        except (IOError, OSError):
            instance = None
        return instance
