# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_dlgfield.py                                                       #
# Purpose: Dialog and form field base classes                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['TextField', 'MultiLineTextField', 'ChoiceField',
           'TextEntry', 'ColourEntry', 'FontEntry']

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.colourselect as CSEL

#-----------------------------------------------------------------------------#

class _LabelField(wx.Panel):
    """Composite control that has a statictext label on the left
    and the given control to one side of it.

    """
    def __init__(self, parent, label, ctor, orient, *cargs, **ckwargs):
        """Create the field
        @param parent: parent window
        @param label: label text
        @param ctor: callable(parent - window object constructor
        @param orient: label position in relation to control (wx.LEFT, ...)
        @note: remaining params are passed to controls ctor

        """
        super(_LabelField, self).__init__(parent)

        # Attributes
        self._lbl = wx.StaticText(self, label=label)
        self._ctrl = ctor(self, *cargs, **ckwargs)

        # Layout
        if orient in (wx.LEFT, wx.RIGHT):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            if orient == wx.LEFT:
                sizer.Add(self._lbl, 0, wx.ALIGN_CENTER_VERTICAL)
                sizer.AddStretchSpacer()
                sizer.Add(self._ctrl, 1, wx.EXPAND|wx.LEFT, 5)
            else:
                sizer.Add(self._ctrl, 1, wx.EXPAND|wx.RIGHT, 5)
                sizer.AddStretchSpacer()
                sizer.Add(self._lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)
            if orient == wx.TOP:
                sizer.Add(self._lbl, 0, wx.ALIGN_LEFT)
                sizer.Add(self._ctrl, 1, wx.EXPAND|wx.TOP, 5)
            else:
                sizer.Add(self._ctrl, 1, wx.EXPAND|wx.BOTTOM, 5)
                sizer.Add(self._lbl, 0, wx.ALIGN_LEFT)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(hsizer)

    FieldCtrl = property(lambda self: self._ctrl)

#-----------------------------------------------------------------------------#

class TextField(_LabelField):
    def __init__(self, parent, label, orient=wx.LEFT):
        super(TextField, self).__init__(parent, label, wx.TextCtrl, orient)

class MultiLineTextField(_LabelField):
    def __init__(self, parent, label, orient=wx.TOP):
        super(MultiLineTextField, self).__init__(parent, label,
                                                 wx.TextCtrl, orient,
                                                 style=wx.TE_MULTILINE)

class ChoiceField(_LabelField):
    def __init__(self, parent, label, orient=wx.LEFT, choices=list()):
        super(ChoiceField, self).__init__(parent, label, wx.TextCtrl,
                                          orient, choices=choices)

#-----------------------------------------------------------------------------#

class NotifierMixin:
    def doNotifyChanged(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

#-----------------------------------------------------------------------------#

class TextEntry(wx.TextCtrl, NotifierMixin):
    def __init__(self, parent, name=u"TextEntry"):
        super(TextEntry, self).__init__(parent, style=wx.TE_PROCESS_ENTER, name=name)

        # Event Handlers
        self.Bind(wx.EVT_TEXT_ENTER, lambda event: self.notifyChanged())
        self.Bind(wx.EVT_KILL_FOCUS, self._onKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self._onSetFocus)

    def _onSetFocus(self, event):
        self.SelectAll()
        event.Skip()

    def _onKillFocus(self, event):
        self.notifyChanged()
        event.Skip()

    def setValue(self, value):
        assert isinstance(value, basestring)
        self.SetValue(value)

    def clear(self):
        self.Clear()

class ColourEntry(CSEL.ColourSelect, NotifierMixin):
    def __init__(self, parent, name=u"ColourEntry"):
        super(ColourEntry, self).__init__(parent, size=(-1, 20))

        # Setup
        self.SetName(name)

        # Event Handlers
        self.Bind(CSEL.EVT_COLOURSELECT, lambda event: self.notifyChanged())
        self.Bind(wx.EVT_SIZE, self._onSize)

    def _onSize(self, event):
        bmp = self.MakeBitmap()
        self.SetBitmap(bmp)
        event.Skip()

    def setValue(self, value):
        assert isinstance(value, wx.Colour)
        if not value.Ok:
            value = wx.BLACK
        self.SetColour(value)

    def clear(self):
        self.SetColour(wx.WHITE)

class FontEntry(wx.FontPickerCtrl, NotifierMixin):
    def __init__(self, parent, name=u"FontEntry"):
        super(FontEntry, self).__init__(parent, size=(-1, 20),
                                        style=wx.FNTP_USEFONT_FOR_LABEL|\
                                              wx.FNTP_FONTDESC_AS_LABEL,
                                        name=name)

        # Event Handlers
        self.Bind(wx.EVT_FONTPICKER_CHANGED, lambda event: self.notifyChanged())

    def setValue(self, value):
        assert isinstance(value, wx.Font)
        self.SetSelectedFont(value)

    def clear(self):
        self.SetSelectedFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
