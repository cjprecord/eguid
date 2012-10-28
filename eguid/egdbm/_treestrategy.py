# -*- coding: utf-8 -*-
###############################################################################
# Name: _treestrategy.py                                                      #
# Purpose: DesignerControl Strategies for Tree controls                       #
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
_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class TreeCtrlStrategy(ControlStrategy):
    """TreeCtrl construction strategy"""
    def __init__(self, name):
        super(TreeCtrlStrategy, self).__init__(name)

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        return name == 'TreeCtrl'

    def postInitSetup(self, control):
        root = control.AddRoot(_("Root"))
        for item in range(4):
            control.AppendItem(root, _("Item %d") % item)
        control.Expand(root)

