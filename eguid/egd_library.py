# -*- coding: utf-8 -*-
###############################################################################
# Name: egd_library.py                                                        #
# Purpose: Designer Library Window UI Components                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Local Imports
import IconResource
import egdgui
from egd_designer import DesignerTLWBase
from egd_designerctrl import DesignerControl
import egd_util
import egd_msg
import egd_libloader

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class LibraryMiniFrame(wx.MiniFrame):
    __metaclass__ = egd_util.Singleton

    def __init__(self, parent, title=u""):
        super(LibraryMiniFrame, self).__init__(parent, title=title,
                                               style=wx.DEFAULT_MINIFRAME_STYLE|\
                                                     wx.SYSTEM_MENU|wx.CLOSE_BOX)

        # Attributes
        self.panel = LibraryPanel(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize((250, 400))

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.Hide()

class LibraryPanel(wx.Panel):
    def __init__(self, parent):
        super(LibraryPanel, self).__init__(parent)

        # Attributes
        self._libraries = wx.Choice(self, choices=["wx",])
        self._ctrlList = LibraryList(self)
        self._search = egdgui.ESearchCtrl(self)
        sbox = wx.StaticBox(self, label=_("Description"))
        self._descbox = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        self._desctxt = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self._busy = None

        # Setup
        self.library = egd_libloader.LibraryLoader()
        wx.CallAfter(self.library.loadDefault)
        self.controlData = list()
        self._ctrlList.setData(list())

        #### SearchCtrl setup
        self._search.doOnKeyUp = self.filterData
        self._search.doOnEnter = self.filterData
        self._search.doOnCancel = lambda event: self._ctrlList.setData(self.controldata)
        self._search.SetDescriptiveText(_("Filter"))

        # Layout
        self.__doLayout()

        # Event Handler
        self.Bind(wx.EVT_CHOICE, self.onLibraryChoice, self._libraries)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onListBox, self._ctrlList)
        self.Bind(wx.EVT_LISTBOX, self.onListSelect, self._ctrlList)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy, self)

        # Message Handlers
        egd_msg.subscribe(self.onStartLoad, egd_msg.EGD_MSG_LOADER_START)
        egd_msg.subscribe(self.onEndLoad, egd_msg.EGD_MSG_LOADER_END)
        egd_msg.subscribe(self.onLoadStatus, egd_msg.EGD_MSG_LOADER_STATUS)

    def onDestroy(self, event):
        egd_msg.unsubscribe(self.onStartLoad)
        egd_msg.unsubscribe(self.onEndLoad)
        egd_msg.unsubscribe(self.onLoadStatus)

    def onStartLoad(self, msg):
        if self._busy is None:
            # TODO: different bitmap
            self._busy = egdgui.BusyDialog(self, IconResource.ControlIcon.Bitmap)
            self._busy.CenterOnScreen()
            self._busy.startBusy() # TODO: handle incremental updates instead
            self._busy.ShowModal()

    def onLoadStatus(self, msg):
        if self._busy:
            self._busy.status = msg.GetData()

    def onEndLoad(self, msg):
        if self._busy:
            self._busy.stopBusy()
            library = self.library.library
            self._libraries.SetItems(sorted(library.keys()))
            self._libraries.SetSelection(0)
            self.controldata = library[self._libraries.GetStringSelection()]
            self._ctrlList.setData(self.controldata)
            self._busy.Destroy()
            self._busy = None

    def onLibraryChoice(self, event):
        """Change the currently selected library"""
        library = self.library.library
        self.controldata = library[self._libraries.GetStringSelection()]
        self._ctrlList.setData(self.controldata)
        self._ctrlList.Refresh()

    def onListBox(self, event):
        """Create the selected control in the current designer"""
        item = self._ctrlList.getItem(event.GetSelection())
        designer = DesignerTLWBase.getActiveDesigner()
        if designer:
            designer.addControl(item.clone())

    def onListSelect(self, event):
        item = self._ctrlList.getItem(event.GetSelection())
        if item:
            doc = getattr(item.Constructor, '__doc__', u"")
            if not isinstance(doc, basestring):
                doc = u""
            # Format the docstring
            # TODO: probably a better way to do this?
            doc = doc.replace(u"\n\n", u"*PARAGRAPH*")
            doc = u" ".join([line.strip() for line in doc.split(u'\n')])
            doc = doc.replace(u"*PARAGRAPH*", u"\n\n")
            self._desctxt.SetValue(doc)

    def filterData(self, event):
        """SearchCtrl callback for key up and enter events"""
        obj = event.GetEventObject()
        value = obj.GetValue()
        if value:
            fdata = [item for item in self.controldata
                     if value.lower() in item.Name.lower() ]
            self._ctrlList.setData(fdata)
        else:
            self._ctrlList.setData(self.controldata)

    def __doLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        chsz = wx.BoxSizer(wx.HORIZONTAL)
        chsz.Add(wx.StaticText(self, label=_("Control Libraries:")), 0,
                 wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 3)
        chsz.Add(self._libraries, 1, wx.EXPAND)
        sizer.Add(chsz, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self._ctrlList, 2, wx.EXPAND)
        sizer.Add(self._search, 0, wx.EXPAND|wx.ALL, 5)
        self._descbox.Add(self._desctxt, 1, wx.EXPAND|wx.ALL, 3)
        sizer.Add(self._descbox, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)

class LibraryList(wx.VListBox):
    def __init__(self, parent):
        super(LibraryList, self).__init__(parent)

        # Attributes
        self._controls = list()

    #---- Virtual overrides ----#

    def OnDrawItem(self, dc, rect, idx):
        """Draw the item"""
        bmp = IconResource.ControlIcon.Bitmap
        dc.DrawBitmap(bmp, rect.x+3, rect.y+3)
        control = self._controls[idx]
        nrect = wx.Rect(*rect)
        nrect.Deflate(bmp.GetWidth() + 6, 0)
        dc.SetTextForeground(wx.BLACK)
        dc.SetFont(self.GetFont())
        dc.DrawLabel(control.Name, nrect, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

    def OnMeasureItem(self, idx):
        """Get the height of the given item"""
        bmp = IconResource.ControlIcon.Bitmap
        return bmp.GetHeight() + 6

    #---- End virtual overrides ----#

    def setData(self, data):
        assert isinstance(data, list)
        self._controls = data
        self.SetItemCount(len(data))
        self.Refresh()

    def getItem(self, index):
        return self._controls[index]

#---- Utilities ----#


