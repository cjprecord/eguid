# -*- coding: utf-8 -*-
###############################################################################
# Name: egd_designer.py                                                       #
# Purpose: Designer UI Components                                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['DesignerDialog', 'DesignerFrame',
           'DesignerMiniFrame', 'DesignerPanel']

#-----------------------------------------------------------------------------#
# Imports
import wx
import inspect
import types

# Local Imports
import egdbm
import IconResource
from egd_inspector import InspectorFrame
import egd_ids
import egd_msg

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class DesignerTLWBase:
    activeDesigner = None
    def __init__(self):
        # Attributes
        self.panel = DesignerPanel(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Events
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onContextMenu)

        # Message Handlers
        egd_msg.subscribe(self.onPropChanged, egd_msg.EGD_MSG_PROP_CHANGED)

    Panel = property(lambda self: self.panel)

    @staticmethod
    def setActiveDesigner(designer):
        DesignerTLWBase.activeDesigner = designer

    @staticmethod
    def getActiveDesigner():
        return DesignerTLWBase.activeDesigner

    def getXml(self):
        """Get the EgdXml object representation of this object
        and all of its descendants.

        """
        xmlobj = egdbm.EgdObject()
        # TODO: generalize
        if isinstance(self, wx.Frame):
            name = "Frame"
        elif isinstance(self, wx.MiniFrame):
            name = "MiniFrame"
        else:
            name = "Dialog"
        xmlobj.name = name
        xmlobj.properties = egdbm.getPropertiesXml(self)
        # Get the DesignerPanels Xml
        xmlobj.objects.append(self.panel.getXml())
        return xmlobj

    def onActivate(self, event):
        if event.Active:
            DesignerTLWBase.setActiveDesigner(self)
        event.Skip()

    def onClose(self, event):
        self.Hide()

    def onContextMenu(self, event):
        """Handle context menu item events from DesignerControl
        right click menus.

        """
        e_id = event.GetId()
        if e_id == egd_ids.ID_INSPECTOR:
            frame = InspectorFrame(self, title=_("Inspector"))
            frame.setDesignerControl(self.panel.getCurrent())
            frame.Show()
        else:
            event.Skip()

    def onPropChanged(self, msg):
        data = msg.GetData()
        field = data.get('field', None)
        if field:
            prop = field.GetName()
            dcontrol = self.Panel.getCurrent()
            if dcontrol:
                instance = dcontrol.Instance
            else:
                # TODO: Log failure to update control
                return

            if hasattr(instance, prop):
                value = data.get('value', None)
                if value:
                    setattr(instance, prop, value)
                    # TODO: this should probably be handled by
                    #       the strategy...
                    instance.SetInitialSize()
                    self.Panel.Refresh()

    def addControl(self, item):
        """Add a control to the designer layout
        @param item: DesignerControl instance

        """
        self.Panel.addControl(item)

class DesignerFrame(wx.Frame,
                    DesignerTLWBase):
    def __init__(self, parent, title=u""):
        wx.Frame.__init__(self, parent, title=title)
        DesignerTLWBase.__init__(self)

    def addControl(self, item):
        """Add a control to the designer layout
        @param item: DesignerControl instance

        """
        name = item.Name
        if name == 'StatusBar':
            if not self.GetStatusBar():
                item.createInstance(self)
                if item.Instance:
                    self.SetStatusBar(item.Instance)
        elif name == 'ToolBar':
            if not self.GetToolBar():
                item.createInstance(self)
                if item.Instance:
                    bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                                   wx.ART_TOOLBAR)
                    item.Instance.AddSimpleTool(wx.ID_ANY, bmp)
                    item.Instance.AddSimpleTool(wx.ID_ANY, bmp)
                    item.Instance.Realize() #TODO move to strategy
                    self.SetToolBar(item.Instance)
        elif name == 'MenuBar':
            if not self.GetMenuBar():
                item.createInstance(self)
                if item.Instance:
                    self.SetMenuBar(item.Instance)
        else:
            # Belongs to the Panel
            super(DesignerFrame, self).addControl(item)

class DesignerDialog(wx.Dialog,
                    DesignerTLWBase):
    def __init__(self, parent, title=u""):
        wx.Dialog.__init__(self, parent, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        DesignerTLWBase.__init__(self)

class DesignerMiniFrame(wx.MiniFrame,
                        DesignerTLWBase):
    def __init__(self, parent, title=u""):
        wx.MiniFrame.__init__(self, parent, title=title,
                              style=wx.DEFAULT_MINIFRAME_STYLE|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        DesignerTLWBase.__init__(self)

ID_RIGHT = wx.NewId()
ID_DOWN = wx.NewId()
ID_LEFT = wx.NewId()
ID_UP = wx.NewId()
class DesignerPanel(wx.PyPanel):
    def __init__(self, parent):
        super(DesignerPanel, self).__init__(parent)

        # Attributes
        self._current = None
        self._designer_controls = list()
        self._designer_menu = None
        self._accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_RIGHT, ID_RIGHT),
                                           (wx.ACCEL_NORMAL, wx.WXK_DOWN, ID_DOWN),
                                           (wx.ACCEL_NORMAL, wx.WXK_LEFT, ID_LEFT),
                                           (wx.ACCEL_NORMAL, wx.WXK_UP, ID_UP),
                                           (wx.ACCEL_NORMAL, wx.WXK_DELETE, wx.ID_DELETE)])

        # Setup
        self.SetAcceleratorTable(self._accel)

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
        ## TODO: Implement control resizing when dragging is done on
        ##       anchor points.
        self.Bind(wx.EVT_MOTION, self.onMotion)
        self.Bind(wx.EVT_MENU, self.onArrowKey, id=ID_RIGHT)
        self.Bind(wx.EVT_MENU, self.onArrowKey, id=ID_DOWN)
        self.Bind(wx.EVT_MENU, self.onArrowKey, id=ID_LEFT)
        self.Bind(wx.EVT_MENU, self.onArrowKey, id=ID_UP)
        self.Bind(wx.EVT_MENU, self.onDeleteCtrl, id=wx.ID_DELETE)

    def onArrowKey(self, event):
        e_id = event.GetId()
        dctrl = self.getCurrent()
        if dctrl:
            # A control is selected so move it
            move_map = { ID_RIGHT : (1, 0), ID_DOWN : (0, 1),
                         ID_LEFT : (-1, 0), ID_UP : (0, -1) }
            adjust = move_map.get(e_id, (0,0))
            dctrl.Instance.Position += adjust
            self.Refresh() # redraw the bounding box

    def onDeleteCtrl(self, event):
        """Remove a control from the layout"""
        dctrl = self.getCurrent()
        if dctrl:
            self.removeControl(dctrl)

    def onContextMenu(self, event):
        if self._designer_menu:
            self._designer_menu.Destroy()
            self._designer_menu = None
        menu = wx.Menu()
        item = wx.MenuItem(menu, egd_ids.ID_INSPECTOR, _("Inspect"))
        item.Bitmap = IconResource.Inspector16.Bitmap
        menu.AppendItem(item)
        self._designer_menu = menu
        self.PopupMenu(menu)

    def onLeftDown(self, event):
        self.clearCurrent()
        self.Refresh()

    def onMotion(self, event):
        if self._current is not None:
            self.SetCursor(self._current.getCursor(event.Position))
        event.Skip()

    def onPaint(self, event):
        dc = wx.PaintDC(self)
        child = self.getCurrent()
        if child:
            ctmp = self._current
            self._current = child
            if child != self._current:
                egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_FOCUS_CHANGED, child)
            self._current.doDrawDecorations(dc)

    def addControl(self, item):
        """Adds a DesignerControl to the panel"""
        item.createInstance(self)
        if item.Instance:
            self._designer_controls.append(item)
            egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_CTRL_ADDED, item)

    def getXml(self):
        """Get the xml for this panel and its children
        @return: EgdObject

        """
        xmlobj = egdbm.EgdObject()
        xmlobj.name = "Panel"
        # TODO: Properties necessary for base panel?
        for ctrl in self._designer_controls:
            xmlobj.objects.append(ctrl.getXml())
        return xmlobj

    def removeControl(self, item):
        """Remove a DesignerControl from the panel"""
        if item in self._designer_controls:
            self._designer_controls.remove(item)
            # Notify that the control was deleted
            egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_CTRL_DELETED, item)
            if self._current is item:
                egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_FOCUS_CHANGED, None)
                self._current = None
            item.Instance.Destroy()
            self.Refresh()

    def clearCurrent(self):
        """Clear the current flag from the current designer control"""
        for child in self.GetChildren():
            child.isCurrent = False

    def getCurrent(self):
        """Get the current designer control"""
        for child in self.GetChildren():
            if getattr(child, 'isCurrent', False):
                for dctrl in self._designer_controls:
                    if child is dctrl.Instance:
                        return dctrl
        return None
