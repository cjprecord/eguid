# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_busy.py                                                           #
# Purpose: Busy Progress Indicator Dialog                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Dialog to indicate that the program is busy performing some task. The dialog
displays an Icon, progress gauge, and a status text field.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['BusyDialog',]

#-----------------------------------------------------------------------------#
# Imports
import wx

#-----------------------------------------------------------------------------#

class BusyDialog(wx.Dialog):
    def __init__(self, parent, bmp):
        super(BusyDialog, self).__init__(parent, style=wx.NO_BORDER)

        # Attributes
        self._panel = BusyPanel(self, bmp)
        self._prog = self._panel.gauge
        self._stat = self._panel.status
        self._timer = wx.Timer(self)

        # Layout
        sizer = wx.BoxSizer()
        sizer.Add(self._panel, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()

        # Event Handlers
        self.Bind(wx.EVT_TIMER, self.onPulse, self._timer)

    def __del__(self):
        self.stopBusy()

    # Properties
    progress = property(lambda self: self._prog.GetValue(),
                        lambda self, val: self._prog.SetValue(val))
    status = property(lambda self: self._stat.GetLabel(),
                      lambda self, stat: self._updateStatus(stat))

    def _updateStatus(self, stat):
        self._stat.SetLabel(stat)
        self._panel.Layout()

    def onPulse(self, event):
        """Animate timer in indeterminate mode"""
        self._prog.Pulse()

    def startBusy(self):
        if not self._timer.IsRunning():
            self._timer.Start(150)

    def stopBusy(self):
        if self._timer.IsRunning():
            self._timer.Stop()
            self.progress = 0

class BusyPanel(wx.Panel):
    def __init__(self, parent, bmp):
        super(BusyPanel, self).__init__(parent)

        # Attributes
        assert isinstance(bmp, wx.Bitmap), "bmp must be a valid wx.Bitmap"
        self._bmp = wx.StaticBitmap(self, bitmap=bmp)
        self._prog = wx.Gauge(self, size=(250, 16), style=wx.GA_HORIZONTAL)
        self._status = wx.StaticText(self, label=u"")

        # Layout
        self.__doLayout()

    # Properties
    gauge = property(lambda self: self._prog)
    status = property(lambda self: self._status)

    def __doLayout(self):
        """Layout the Panel"""
        vsizer = wx.BoxSizer(wx.VERTICAL)

        vsizer.Add((20,20))
        vsizer.Add(self._bmp, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        vsizer.Add(self._prog, 1, wx.EXPAND|wx.ALL, 5)
        vsizer.Add(self._status, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        vsizer.Add((20,20))

        self.SetSizer(vsizer)
