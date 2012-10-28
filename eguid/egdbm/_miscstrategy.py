# -*- coding: utf-8 -*-
###############################################################################
# Name: _miscstrategy.py                                                      #
# Purpose: DesignerControl Strategies for Misc controls                       #
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

from eguid import IconResource

#-----------------------------------------------------------------------------#

class HyperLinkCtrlStrategy(ControlStrategy):
    """HyperLinkCtrl construction strategy"""
    def __init__(self, name):
        super(HyperLinkCtrlStrategy, self).__init__(name)

    def getArgs(self):
        return [wx.ID_ANY, self.name, u"http://someurl.com"]

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name == 'HyperlinkCtrl'

    def postInitSetup(self, control):
        # Prevent link clicks from activating the browser
        control.Bind(wx.EVT_HYPERLINK, lambda event: event.StopPropagation())

#-----------------------------------------------------------------------------#

class BitmapCtrlStrategy(ControlStrategy):
    """StaticBitmap/BitmapButton construction strategy"""
    def __init__(self, name):
        super(BitmapCtrlStrategy, self).__init__(name)

    def getKWArgs(self):
        return dict(bitmap=IconResource.GenericImage.Bitmap)

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name in ('StaticBitmap', 'BitmapButton')

    def postInitSetup(self, control):
        control.SetInitialSize()

#-----------------------------------------------------------------------------#

class StaticLineStrategy(ControlStrategy):
    """StaticBitmap/BitmapButton construction strategy"""
    def __init__(self, name):
        super(StaticLineStrategy, self).__init__(name)

    def getKWArgs(self):
        return dict(pos=(20,20), size=(100, -1), style=wx.LI_HORIZONTAL)

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name in ('StaticLine',)
