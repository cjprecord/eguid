# -*- coding: utf-8 -*-
###############################################################################
# Name: _menustrategy.py                                                      #
# Purpose: DesignerControl Strategies for Menus and MenuBars                  #
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
from controlstrategy import ControlStrategy

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class MenuBarStrategy(ControlStrategy):
    """MenuBar construction strategy"""
    def __init__(self, name):
        super(MenuBarStrategy, self).__init__(name)

    def getArgs(self):
        return []

    def getKWArgs(self):
        return dict()

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name == 'MenuBar'

    def initInstance(self, ctor, parent):
        return ctor()

    def postInitSetup(self, control):
        control.Append(wx.Menu(), _("File"))
