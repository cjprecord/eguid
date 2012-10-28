# -*- coding: utf-8 -*-
###############################################################################
# Name: _radioboxstrategy.py                                                  #
# Purpose: DesignerControl Strategy for RadioBox                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import wx #TODO: needed when initInstance is called by base class
from controlstrategy import ControlWithLabelStrategy, WrapperPanel

#-----------------------------------------------------------------------------#

class StaticBoxStrategy(ControlWithLabelStrategy):
    """Common control construction strategy for most controls"""
    def __init__(self, name):
        super(StaticBoxStrategy, self).__init__(name)

    def initInstance(self, ctor, parent=None):
        """Create an instance of the class object
        @param ctor: class constructor function
        @keyword parent: parent window the control belongs to
        @return: control instance

        """
        panel = WrapperPanel(parent, ctor, *self.getArgs(), **self.getKWArgs())
        return panel

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name == 'StaticBox'

#-----------------------------------------------------------------------------#

class RadioBoxStrategy(ControlWithLabelStrategy):
    """Common control construction strategy for most controls"""
    def __init__(self, name):
        super(RadioBoxStrategy, self).__init__(name)

    def getKWArgs(self):
        bdict = super(RadioBoxStrategy, self).getKWArgs()
        # Constructor requires some choices to be set
        rdict = dict(choices=["RadioButton %d" % x for x in range(3)],
                     style=wx.RA_VERTICAL)
        rdict.update(bdict)
        return rdict

    def initInstance(self, ctor, parent=None):
        """Create an instance of the class object
        @param ctor: class constructor function
        @keyword parent: parent window the control belongs to
        @return: control instance

        """
        panel = WrapperPanel(parent, ctor, *self.getArgs(), **self.getKWArgs())
        return panel

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name == 'RadioBox'
