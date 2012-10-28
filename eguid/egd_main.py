# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_main.py                                                           #
# Purpose: Main Designer Program UI                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.agw.aui as aui

# Local Imports
import IconResource
from egd_library import LibraryMiniFrame
from egd_designer import *
import egd_inspector
import egd_projtree
import egd_ids
import egd_cfg
import egd_msg

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class EGUIDFrame(wx.Frame):
    def __init__(self, parent):
        super(EGUIDFrame, self).__init__(parent)

        # Attributes
        self._mgr = aui.AuiManager(self)
        self.tree = egd_projtree.ProjectTree(self)
        pane = aui.AuiPaneInfo().Center().Name(u"ProjectTree")
        pane = pane.CaptionVisible(False)
        self._mgr.AddPane(self.tree, pane)
        self.panel = EGUIDPanel(self)
        pane2 = aui.AuiPaneInfo().Center().Name(u"TopLevelObjects")
        pane2 = pane2.Caption(_("Templates"))
        self._mgr.AddPane(self.panel, pane2)
        wx.CallAfter(self._mgr.Update)

        # Setup Menus
        # TODO: move all menu setup out into own class or elsewhere
        mb = wx.MenuBar()
        ## File Menu
        fmenu = wx.Menu()
        item = fmenu.Append(wx.ID_NEW, _("&New Project") + "\tCtrl+N")
        self.Bind(wx.EVT_MENU, self.onNew, item)
        item = fmenu.Append(wx.ID_OPEN, _("&Open Project") + "\tCtrl+O")
        self.Bind(wx.EVT_MENU, self.onOpen, item)
        fmenu.AppendSeparator()
        item = fmenu.Append(wx.ID_SAVE, _("&Save") + "\tCtrl+S")
        self.Bind(wx.EVT_MENU, self.onSave, item)
        item = fmenu.Append(wx.ID_SAVEAS, _("Save &As") + "\tCtrl+Shift+S")
        self.Bind(wx.EVT_MENU, self.onSaveAs, item)
        fmenu.AppendSeparator()
        item = fmenu.Append(wx.ID_EXIT, _("E&xit") + "\tCtrl+Q")
        self.Bind(wx.EVT_MENU, self.onExit, item)
        mb.Append(fmenu, _("&File"))

        ## Tools Menu
        tmenu = wx.Menu()
        item = wx.MenuItem(tmenu, egd_ids.ID_LIBRARY, _("Library") + "\tCtrl+L")
        item.Bitmap = IconResource.Library16.Bitmap
        tmenu.AppendItem(item)
        tmenu.AppendSeparator()
        item = wx.MenuItem(tmenu, egd_ids.ID_INSPECTOR, _("Inspector") + "\tCtrl+I")
        item.Bitmap = IconResource.Inspector16.Bitmap
        tmenu.AppendItem(item)
        mb.Append(tmenu, _("&Tools"))

        self.SetMenuBar(mb)

        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize((300, 300))

        # Event Handlers
        self.Bind(wx.EVT_MENU, self.onInspect, id=egd_ids.ID_INSPECTOR)
        self.Bind(wx.EVT_MENU, self.onLibrary, id=egd_ids.ID_LIBRARY)

        # Load last project?
        # TODO:
        
        self.updateTitle()

    #---- Event Handlers ----#

    def onInspect(self, event):
        """Open the inspector dialog"""
        iframe = egd_inspector.InspectorFrame(self, _("Inspector"))
        # TODO: try to make sure it isn't placed over the top of the currently
        #       active designer window if possible.
        iframe.Show()

    def onLibrary(self, event):
        """Open the control library dialog"""
        lframe = LibraryMiniFrame(self, _("Control Library"))
        # TODO: try to make sure it isn't placed over the top of the currently
        #       active designer window if possible.
        lframe.Show()

    def onExit(self, event):
        # TODO: Check for modifications and prompt to save
        # TODO: Store user configuration
        self.Close()

    def onNew(self, event):
        """Handle creating a new project"""
        # TODO:
        pass

    def onOpen(self, event):
        """Handle open request"""
        # TODO: Implement open feature when serialization format is decided
        pass

    def onSave(self, event):
        # TODO: Implement saving
        self.tree.saveProject()

    def onSaveAs(self, event):
        # TODO: implement save as
        pass

    #---- Implementation ----#

    def updateTitle(self):
        """Update the Frames title"""
        # TODO: update for project name "Equid - Project name"
        self.SetTitle(_("Eguid"))

class EGUIDPanel(wx.Panel):
    def __init__(self, parent):
        super(EGUIDPanel, self).__init__(parent)

        # Attributes
        self._list = ULC.UltimateListCtrl(self, wx.ID_ANY,
                                          agwStyle=wx.LC_ICON|\
                                                   ULC.ULC_STICKY_HIGHLIGHT|\
                                                   ULC.ULC_SEND_LEFTCLICK|\
                                                   ULC.ULC_STICKY_NOSELEVENT)

        # Setup
        self._list.EnableSelectionVista(True)
        il = wx.ImageList(32, 32)
        il.Add(IconResource.NewWindow.Bitmap)
        self._list.AssignImageList(il, wx.IMAGE_LIST_NORMAL)
        # TODO: create/use an observer interface to allow extensions
        #       to populate the recipe list
        self._list.InsertImageStringItem(0, _("New Frame"), 0)
        self._list.SetItemData(0, lambda: self.createNewDesigner("Frame"))
        self._list.InsertImageStringItem(1, _("New MiniFrame"), 0)
        self._list.SetItemData(1, lambda: self.createNewDesigner("MiniFrame"))
        self._list.InsertImageStringItem(2, _("New Dialog"), 0)
        self._list.SetItemData(2, lambda: self.createNewDesigner("Dialog"))
        # TODO: support creating panels in designer mode
        self._list.InsertImageStringItem(3, _("New Panel"), 0)
        self._list.SetItemData(3, lambda: self.createNewDesigner("Panel"))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Event handlers
        self.Bind(ULC.EVT_LIST_ITEM_LEFT_CLICK, self.onItemSelected, self._list)

    def onItemSelected(self, event):
        """Create a new designer window"""
        index = event.m_itemIndex
        activator = self._list.GetItemData(index)
        if callable(activator):
            wx.CallAfter(activator)

    def createNewDesigner(self, designer):
        clsmap = dict(Frame=lambda parent: DesignerFrame(parent, title=_("Frame Designer")),
                      Dialog=lambda parent: DesignerDialog(parent, title=_("Dialog Designer")),
                      MiniFrame=lambda parent: DesignerMiniFrame(parent, title=_("MiniFrame Designer")))
        ctor = clsmap.get(designer,None)
        if ctor:
            parent = self.GetTopLevelParent()
            win = ctor(parent)
            win.Show()
            # Notify that new designer was created
            egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_NEW_WINDOW, win)

#-----------------------------------------------------------------------------#

class EGUIDApp(wx.App):
    def OnInit(self):
        self.SetAppName("Eguid")

        # Init Configuration
        cfg = egd_cfg.EgdConfig()
        if not cfg.hasConfigDir("library"):
            cfg.makeConfigDir("library")

        # Initialize Application
        self.frame = EGUIDFrame(None)
        self.frame.Show()
        self._library = LibraryMiniFrame(self.frame, _("Control Library"))
        rect = self.frame.GetRect()
        self._library.SetPosition((rect.x + rect.width, rect.y))
        self._library.Show()

        # Initialize singletons
        inspector = egd_inspector.InspectorFrame(self.frame,
                                                 title=_("Inspector"))
        inspector.Hide()

        return True

def main():
    app = EGUIDApp(False)
    app.MainLoop()

