# -*- coding: utf-8 -*-
###############################################################################
# Name: controlstrategy.py                                                    #
# Purpose: DesignerControl Strategies                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['ESearchCtrl',]

#-----------------------------------------------------------------------------#
# Imports
import wx

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ESearchCtrl(wx.SearchCtrl):
    """Search Control"""
    def __init__(self, parent, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name="ESearchCtrl"):

        clone = None
        if validator != wx.DefaultValidator:
            clone = validator.Clone()

        super(ESearchCtrl, self).__init__(parent, id, value, pos,
                                          size, style, validator, name)

        # Attributes
        self._txtctrl = None  # For msw/gtk
        #### Callback observers callable(event)
        self.doOnKeyUp = None
        self.doOnEnter = None
        self.doOnKeyDown = None
        self.doOnCancel = None

        # Hide the search button and text by default
        self.ShowSearchButton(True)
        self.ShowCancelButton(True)
        self.SetDescriptiveText(_("Search"))

        # MSW/GTK HACK need to bind directly to the text control component
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    if clone is not None:
                        child.SetValidator(clone)
                    self._txtctrl = child
                    child.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
                    child.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
                    break
        else:
            self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        # Event management
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)

    def GetTextControl(self):
        """Get the wx.TextCtrl window.
        @note: only for msw/gtk

        """
        return self._txtctrl

    def OnCancel(self, event):
        self.Clear()
        if self.doOnCancel:
            self.doOnCancel(event)

    def OnKeyDown(self, evt):
        """Handle KeyDown events"""
        if self.doOnKeyDown:
            self.doOnKeyDown(evt)
        else:
            evt.Skip()

    def OnKeyUp(self, evt):
        """Handle KeyUp events"""
        if self.doOnKeyUp:
            self.doOnKeyUp(evt)
        else:
            evt.Skip()

    def OnEnter(self, evt):
        """Handle the Enter key event"""
        if self.doOnEnter:
            self.doOnEnter(evt)
        else:
            evt.Skip()

    def SetFocus(self):
        """Set the focus and select the text in the field"""
        super(ESearchCtrl, self).SetFocus()
        self.SelectAll()
