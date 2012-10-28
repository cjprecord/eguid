###############################################################################
# Name: testEgdLibrary.py                                                     #
# Purpose: Unit tests for the designer control library xml classes.           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the Library Serialization Xml"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision: $"

#-----------------------------------------------------------------------------#
# Imports
import unittest

import common

# Module to test
from eguid import egdbm

#-----------------------------------------------------------------------------#
# Test Class

class EgdLibraryTest(unittest.TestCase):
    """Tests the Eguid Library Xml classes"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    #---- Tests ----#

    def testControl(self):
        """Test the control xml"""
        h = egdbm.EgdControl.parse("<control name='ListCtrl' module='wx'/>")
        self.assertTrue(h)
        self.assertEquals(h.name, "ListCtrl")
        self.assertEquals(h.module, "wx")

    def testLibrary(self):
        """Test the Library"""
        xmlstr = "<library name='wx' version='2.8.11.0'><control name='ListCtrl' module='wx'/></library>"
        h = egdbm.EgdLibrary.parse(xmlstr)
        self.assertTrue(h)
        self.assertEquals(h.name, 'wx')
        self.assertEquals(len(h.controls), 1)
        ## Check the control
        ctrl = h.controls[0]
        self.assertEquals(ctrl.name, 'ListCtrl')
