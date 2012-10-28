# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_foldpanel.py                                                      #
# Purpose: FoldPanel Container Class                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['FoldPanelMgr', 'FoldPanelBase']

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.agw.foldpanelbar as FPB

#-----------------------------------------------------------------------------#

class FoldPanelMgr(FPB.FoldPanelBar):
    """Fold panel that manages a collection of Panels"""
    def __init__(self, parent, *args, **kwargs):
        super(FoldPanelMgr, self).__init__(parent, *args, **kwargs)

    def addPanel(self, pclass, title=u"", collapsed=False):
        """Add a panel to the manager
        @param pclass: Class constructor (callable)
        @keyword title: foldpanel title
        @keyword collapsed: start with it collapsed
        @return: pclass instance
        """
        fpitem = self.AddFoldPanel(title, collapsed=collapsed)
        wnd = pclass(fpitem)
        best = wnd.GetBestSize()
        wnd.SetSize(best)
        self.AddFoldPanelWindow(fpitem, wnd)
        return wnd

#-----------------------------------------------------------------------------#

class FoldPanelBase(wx.Panel):
    """Base Panel control used by FoldPanelMgr"""
    def __init__(self, parent):
        super(FoldPanelBase, self).__init__(parent)

        # Layout
        self.doLayout()

    def doLayout(self):
        """Override in subclass"""
        pass


