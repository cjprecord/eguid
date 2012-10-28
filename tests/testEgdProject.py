###############################################################################
# Name: testEgdProject.py                                                     #
# Purpose: Unit tests for the Project Xml classes                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the Project Xml"""

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

class EgdProjectTest(unittest.TestCase):
    """Tests the Eguid Project Xml class"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    #---- Tests ----#

    def testProperty(self):
        # Basic parsing tests
        h = egdbm.EgdProperty.parse("<property name='foo' value='bar'/>")
        self.assertTrue(h)
        self.assertEquals(h.name, 'foo')
        self.assertEquals(h.value, 'bar')

        h = egdbm.EgdProperty.parse("<property name='bar' value='foo'></property>")
        self.assertTrue(h)
        self.assertEquals(h.name, 'bar')
        self.assertEquals(h.value, 'foo')

        # Test Parsing Errors
        # 1) name attribute is required
        self.assertRaises(egdbm.ParseError,
                          egdbm.EgdProperty.parse,"<property></property>")

    def testObject(self):
        # Basic parsing test
        h = egdbm.EgdObject.parse("<object name='Button' module='wx'/>")
        self.assertTrue(h)
        self.assertEquals(h.name, 'Button')
        self.assertEquals(h.module, 'wx')

        # Test parsing object that has properties
        h = egdbm.EgdObject.parse("<object name='Button' module='wx'>"
                                     "<property name='Size' value='(100,100)'/>"
                                  "</object>")
        self.assertTrue(h)
        self.assertEquals(len(h.properties), 1)
        prop = h.properties[0]
        self.assertEquals(prop.name, 'Size')
        self.assertTrue(isinstance(prop.value, tuple))
        self.assertEquals(prop.value, (100,100))

        # Test recursive nesting
        xmlstr = """<object name='Frame' module='wx'>
                       <property name='Size' value='(100,100)'/>
                       <object name='Panel' module='wx'>
                           <object name='Button' module='wx'>
                               <property name='Label' value='Push Me'/>
                           </object>
                       </object>
                    </object>
                    """
        h = egdbm.EgdObject.parse(xmlstr)
        self.assertTrue(h)
        self.assertEquals(h.name, 'Frame')
        self.assertEquals(h.module, 'wx')
        self.assertEquals(len(h.properties), 1)
        # Check the object's Property
        prop = h.properties[0]
        self.assertEquals(prop.name, 'Size')
        self.assertEquals(prop.value, (100,100))
        # Check the object's objects
        self.assertEquals(len(h.objects), 1)
        obj = h.objects[0]
        self.assertEquals(obj.name, 'Panel')
        self.assertEquals(obj.module, 'wx')
        ## Check that the object nested in the object was found
        self.assertEquals(len(obj.objects), 1)
        obj2 = obj.objects[0]
        self.assertEquals(obj2.name, 'Button')
        self.assertEquals(obj2.module, 'wx')
        ## Now check its properties
        self.assertEquals(len(obj2.properties), 1)
        prop2 = obj2.properties[0]
        self.assertEquals(prop2.name, 'Label')
        self.assertEquals(prop2.value, 'Push Me')

        # Test assignment
        obj = egdbm.EgdObject(name="TextCtrl", module="wx")
        self.assertEquals(obj.name, "TextCtrl")
        self.assertEquals(obj.module, "wx")
        obj.properties = [ egdbm.EgdProperty(name="Size", value=(100,20)),]
        xmlstr = '<?xml version="1.0" ?><object name="TextCtrl" module="wx"><property name="Size" value="(100, 20)" /></object>'
        self.assertEquals(xmlstr, obj.render())

        # Test Parsing Errors
        # 1) name attribute is required
        self.assertRaises(egdbm.ParseError,
                          egdbm.EgdObject.parse,"<object module='wx'/>")
        # 2) module attribute is required
        self.assertRaises(egdbm.ParseError,
                          egdbm.EgdObject.parse,"<object name='Choice'/>")
        # 3) Test with all required fields missing
        self.assertRaises(egdbm.ParseError,
                          egdbm.EgdObject.parse,"<object/>")

    def testProject(self):
        """Test the main Project object"""
        pxml = common.getDataFileContents("project.xml")
        h = egdbm.EgdProject.parse(pxml)
        self.assertTrue(h)

    def testVersion(self):
        """Test the version tag"""
        h = egdbm.EgdVersion.parse("<version major='1' minor='0'/>")
        self.assertTrue(h)
        self.assertEquals(h.major, 1)
        self.assertEquals(h.minor, 0)
