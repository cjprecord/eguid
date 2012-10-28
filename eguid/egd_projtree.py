# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_projtree.py                                                       #
# Purpose: Project Display Tree                                               #
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
import wx.lib.agw.customtreectrl as CT

# Local Imports
import IconResource
import egdbm
import egd_ids
import egd_msg
import egd_designerctrl

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ProjectTree(CT.CustomTreeCtrl):
    """Tree to display a designer projects components"""
    # Icon indexes
    ICON_MAIN_COMPONENT, \
    ICON_SUB_COMPONENT, \
    ICON_ACTION_CONTROLLER = range(3)
    def __init__(self, parent):
        super(ProjectTree, self).__init__(parent,
                                          agwStyle=CT.TR_SINGLE|\
                                                   CT.TR_HIDE_ROOT|\
                                                   CT.TR_FULL_ROW_HIGHLIGHT|\
                                                   CT.TR_HAS_BUTTONS|\
                                                   CT.TR_FULL_ROW_HIGHLIGHT)

        # Attributes
        self._il = wx.ImageList(16,16)
        self._project = None
        self._menu = None

        # Setup
        self._setupImageList()
        self.EnableSelectionVista(True)
        self._root = self.AddRoot("ProjectRoot")

        # Event Handlers
        self.Bind(CT.EVT_TREE_SEL_CHANGED, self.onItemSelected)
        self.Bind(CT.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
        self.Bind(CT.EVT_TREE_ITEM_RIGHT_CLICK, self.onItemRClick)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy, self)

        # Message Handlers
        egd_msg.subscribe(self.onCtrlAdded, egd_msg.EGD_MSG_DESIGNER_CTRL_ADDED)
        egd_msg.subscribe(self.onCtrlDeleted, egd_msg.EGD_MSG_DESIGNER_CTRL_DELETED)
        egd_msg.subscribe(self.onNewDesigner, egd_msg.EGD_MSG_DESIGNER_NEW_WINDOW)
        egd_msg.subscribe(self.onCtrlChanged, egd_msg.EGD_MSG_DESIGNER_FOCUS_CHANGED)

    def _setupImageList(self):
        """Setup the tree's ImageList"""
        # Maintenance Note: If order is changed the ICON_FOO identifiers
        #                   in this class must be updated as well.
        self._il.Add(IconResource.MainComponent16.Bitmap)
        self._il.Add(IconResource.SubComponent16.Bitmap)
        self._il.Add(IconResource.ActionController16.Bitmap)
        self.SetImageList(self._il)

    def _destroyMenu(self):
        if self._menu is not None:
            self._menu.Destroy()
            self._menu = None

    #---- Properties ----#

    #---- Event Handlers ----#

    def onDestroy(self, event):
        self._destroyMenu()
        egd_msg.unsubscribe(self.onCtrlAdded)
        egd_msg.unsubscribe(self.onCtrlDeleted)
        egd_msg.unsubscribe(self.onNewDesigner)
        egd_msg.unsubscribe(self.onCtrlChanged)

    def onItemRClick(self, event):
        """Show the context menu for the item"""
        self._destroyMenu()
        item = event.GetItem()
        self._menu = wx.Menu()
        if self.ItemHasChildren(item):
            # TODO: need special items for a tlw?
            pass
        item = wx.MenuItem(self._menu, egd_ids.ID_INSPECTOR, _("Inspect"))
        item.Bitmap = IconResource.Inspector16.Bitmap
        self._menu.AppendItem(item)
        self._menu.AppendSeparator()
        self._menu.Append(wx.ID_DELETE, _("Delete"))
        self.PopupMenu(self._menu)

    def onItemActivated(self, event):
        """Item was double clicked on"""
        item = event.GetItem()
        dctrl = self.GetPyData(item)
        if self.ItemHasChildren(item):
            # Designer Window
            if not dctrl.IsShown():
                dctrl.Show()
            dctrl.Raise()
        else:
            dctrl.Instance.setCurrent()

    def onItemSelected(self, event):
        """Select the item in the designer window that
        is selected in the tree.

        """
        item = event.GetItem()
        dctrl = self.GetPyData(item)
        if self.ItemHasChildren(item):
            # Is a designer object
            if dctrl.IsShown():
                dctrl.Raise()
        else:
            dctrl.Instance.setCurrent()

    #---- Message Handlers ----#

    def onCtrlAdded(self, msg):
        """Handle updating the tree when a control is added"""
        # The message data is a DesignerControl object
        dctrl = msg.GetData()
        if dctrl:
            self.addDesignerControl(dctrl)

    def onCtrlDeleted(self, msg):
        """Control deleted from the designer window"""
        dctrl = msg.GetData()
        if not dctrl:
            return
        node = self.findItem(dctrl)
        if node:
            self.Delete(node)

    def onNewDesigner(self, msg):
        """New designer window was created"""
        # Data is a DesignerWindow (TODO: currently just tlw ref)
        dwin = msg.GetData()
        if dwin:
            self.addDesignerWindow(dwin)

    def onCtrlChanged(self, msg):
        """Selected control in the current designer window has changed"""
        return #TODO: recursion issue....
#        dctrl = msg.GetData()
#        if dctrl is None:
#            return
#        node = self.findParentNode(dctrl)
#        if node:
#            cnode = self.GetFirstChild(node)[0]
#            while cnode:
#                nchild = self.GetPyData(cnode)
#                if nchild is dctrl:
#                    self.Expand(node)
#                    self.SelectItem(cnode)
#                else:
#                    cnode = self.GetNextSibling(cnode)

    #---- Overrides ----#

    def SelectItem(self, item):
        """Override SelectItem to prevent it from sending selection events"""
        self.Unbind(CT.EVT_TREE_SEL_CHANGED)
        super(ProjectTree, self).SelectItem(item)
        self.Bind(CT.EVT_TREE_SEL_CHANGED, self.onItemSelected)

    #---- Implementation ----#

    def addDesignerControl(self, dctrl):
        """Add a new designer control to the project"""
        node = self.findParentNode(dctrl)
        if node:
            data = self.GetPyData(node)
            self.SetItemHasChildren(node)
            # TODO: check for WrapperPanel
            item = self.AppendItem(node, dctrl.Instance.GetName(),
                                   image=ProjectTree.ICON_SUB_COMPONENT)
            self.SetPyData(item, dctrl)
            self.Expand(node)
            self.SelectItem(item)
        # TODO: replace with log statement
        assert node is not None, "%s: Not added to project!!" % repr(dctrl)

    def addDesignerWindow(self, dwin):
        """Add a new toplevel designer window to the project"""
        item = self.AppendItem(self._root, dwin.GetTitle(),
                               image=ProjectTree.ICON_MAIN_COMPONENT)
        self.SetItemHasChildren(item, True)
        self.SetPyData(item, dwin) # Store ref to designer

    def findItem(self, dctrl):
        """Find the TreeItem associated with the given DesignerControl"""
        rItem = None
        node = self.findParentNode(dctrl)
        if node:
            cnode = self.GetFirstChild(node)[0]
            while cnode:
                nchild = self.GetPyData(cnode)
                if nchild is dctrl:
                    rItem = cnode
                    break
                else:
                    cnode = self.GetNextSibling(cnode)
        return rItem

    def findParentNode(self, dctrl):
        """Find the DesignerWindow parent node for the given DesignerControl"""
        assert isinstance(dctrl, egd_designerctrl.DesignerControl)
        inst = dctrl.Instance
        assert inst, "DesignerControl not instantiated!"
        # Find the designer window that the control belongs to
        tlw = inst.GetTopLevelParent()
        bFound = False
        node = self.GetFirstChild(self._root)[0]
        while node:
            data = self.GetPyData(node)
            if data is tlw:
                bFound = True
                break
            else:
                node = self.GetNextSibling(node)

        if not bFound:
            node = None
        return node

    def saveProject(self):
        """Save the project"""
        # TODO: handle protocol versioning more globally?
        verxml = egdbm.EgdVersion()
        verxml.major = 1
        verxml.minor = 0
        # Construct the project XML
        projxml = egdbm.EgdProject()
        projxml.name = "TestProject" # TODO: get from user save/new proj
        # Walk all root objects
        node = self.GetFirstChild(self._root)[0]
        while node:
            if self.HasChildren(node):
                data = self.GetPyData(node)
                projxml.objects.append(data.getXml())
            node = self.GetNextSibling(node)
        print projxml.getPrettyXml()

    def loadProject(self, proj):
        """Load a project in to the view"""
        raise NotImplementedError
