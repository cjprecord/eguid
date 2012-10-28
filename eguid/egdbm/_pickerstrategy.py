# -*- coding: utf-8 -*-
###############################################################################
# Name: _pickerstrategy.py                                                    #
# Purpose: DesignerControl Strategies for Picker Controls                     #
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

#-----------------------------------------------------------------------------#

class PickerStrategy(ControlStrategy):
    """PickerCtrl construction strategy"""
    def __init__(self, name):
        super(PickerStrategy, self).__init__(name)

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        cobj = getattr(module, name)
        return issubclass(cobj, wx.PickerBase)

    def postInitSetup(self, control):
        # Prevent any popup dialogs from being shown due to button clicks
        # while dragging the control around the designer.
        for child in control.GetChildren():
            if isinstance(child, wx.Button):
                child.Bind(wx.EVT_BUTTON, lambda event: event.StopPropagation())
