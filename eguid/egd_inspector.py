# -*- coding: utf-8 -*-
###############################################################################
# Name: egd_inspector.py                                                      #
# Purpose: Designer Inspector Window                                          #
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
import wx.lib.agw.labelbook as LB
import wx.lib.agw.foldpanelbar as FPB

# Local imports
import IconResource
import egd_util
from egd_designerctrl import DesignerControl
import egdgui
import egd_msg

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class InspectorFrame(wx.MiniFrame):
    """Window for inspecting and editing a controls properties"""
    __metaclass__ = egd_util.Singleton

    def __init__(self, parent, title=u""):
        style=wx.DEFAULT_MINIFRAME_STYLE|wx.SYSTEM_MENU|wx.CLOSE_BOX
        super(InspectorFrame, self).__init__(parent, title=title, style=style)

        # Attributes
        self._designerCtrl = None
        self._book = InspectorBook(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._book, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Event Handlers
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Message handlers
        egd_msg.subscribe(self.onControlChanged,
                          egd_msg.EGD_MSG_DESIGNER_FOCUS_CHANGED)

    def setDesignerControl(self, dcontrol):
        """Set the control that is actively being inspected
        @param dcontrol: L{DesignerControl}

        """
        self._designerCtrl = dcontrol
        self._book.setActiveControl(dcontrol)

    def onClose(self, event):
        """Handle when the dialog closes"""
        # TODO: check for possibly un-applied setting changes
        # NOTE: may not be necessary as all or most settings should be
        #       applied immediately.
        self.Hide()

    def onShow(self, event):
        self._book.setActiveControl(self._designerCtrl)
        event.Skip()

    def onControlChanged(self, msg):
        """The control that was selected in the designer has changed"""
        data = msg.GetData()
        self.setDesignerControl(data)

#-----------------------------------------------------------------------------#

class InspectorBook(LB.FlatImageBook):
    def __init__(self, parent):
        style = LB.INB_FIT_BUTTON|LB.INB_SHOW_ONLY_IMAGES
        super(InspectorBook, self).__init__(parent, agwStyle=style)

        # Attributes
        self._activeCtrl = None
        self._props = PropertiesPanel(self)

        # Setup
        imglst = wx.ImageList(16, 16)
        propidx = imglst.Add(IconResource.Preferences16.Bitmap)
        self.AssignImageList(imglst)
        ## Add the pages
        self.AddPage(self._props, _("Properties"), True, propidx)

    def setActiveControl(self, ctrl):
        """Set the active designer control
        @param ctrl: L{DesignerControl}

        """
        self._activeCtrl = ctrl
        # Update all pages
        for page in (self._props,):
            if page:
                page.setControl(ctrl)

#-----------------------------------------------------------------------------#

class InspectorPanelBase(wx.PyPanel):
    def __init__(self, parent):
        super(InspectorPanelBase, self).__init__(parent)

        # Attributes
        self._fields = dict() # Collection of Standard Controls
        self._ctrl = None

    Control = property(lambda self: self._ctrl,
                       lambda self, ctrl: self.setControl(ctrl))
    Fields = property(lambda self: self._fields)

    #---- Implementation ----#

    def clearFields(self):
        """Resets all fields for when no DesignerControl is selected"""
        for prop in self.Fields:
            field = self.getFieldControl(prop)
            field.clear()

    def enableFields(self, enable=True):
        """Enable/disable all fields"""
        for prop in self.Fields:
            field = self.getFieldControl(prop)
            field.Enable(enable)

    def updateFields(self):
        """Updates all fields for when a new DesignerControl is selected"""
        instance = self.Control.Instance
        for prop in self.Fields:
            field = self.getFieldControl(prop)
            if field:
                val = getattr(instance, prop)
                field.setValue(getattr(instance, prop))

    def setControl(self, control):
        """"Set the control actively being inspected
        @param control: L{DesignerControl}

        """
        if control:
            assert isinstance(control, DesignerControl)
            self._ctrl = control
            self.enableFields(True)
            self.updateFields()
        else:
            self.clearFields()
            self.enableFields(False)

    def addFieldControl(self, name, ctrl):
        assert name not in self._fields
        self._fields[name] = ctrl

    def getFieldControl(self, name):
        return self._fields.get(name, None)

#-----------------------------------------------------------------------------#

class PropertiesPanel(InspectorPanelBase):
    """Main control properties panel in notebook"""
    def __init__(self, parent):
        super(PropertiesPanel, self).__init__(parent)

        # Attributes
        self.fpb = egdgui.FoldPanelMgr(self, agwStyle=FPB.FPB_VERTICAL)

        # Message Handlers
        egd_msg.subscribe(self.onRegProperty, egd_msg.EGD_MSG_REG_PROP)

        # Setup
        self.fpb.addPanel(GeneralFoldPanel, _("General"), False)
        self.fpb.addPanel(StyleFoldPanel, _("Visual"), False)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.fpb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def onRegProperty(self, msg):
        datadict = msg.GetData()
        for name, fieldctrl in datadict.iteritems():
            self.addFieldControl(name, fieldctrl)

#-----------------------------------------------------------------------------#

class GeneralFoldPanel(egdgui.FoldPanelBase):
    def doLayout(self):
        sizer = wx.FlexGridSizer(0, 2, 3, 8)
        fields = (('Name', _("Name")), ('Label', _("Label")))
        for prop, lbl in fields:
            label = wx.StaticText(self, label=lbl)
            sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            field = PropertyTextField(self, name=prop)
            sizer.Add(field, 1, wx.EXPAND)
            egd_msg.sendMessage(egd_msg.EGD_MSG_REG_PROP, data={prop:field})

        sizer.AddGrowableCol(1, 1)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        self.SetSizer(hsizer)

class StyleFoldPanel(egdgui.FoldPanelBase):
    def doLayout(self):
        sizer = wx.FlexGridSizer(0, 2, 3, 8)
        # Add some fields for modifying the colour
        fields = (('ForegroundColour', _("Foreground")),
                  ('BackgroundColour', _("Background")))
        for prop, lbl in fields:
            label = wx.StaticText(self, label=lbl)
            sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            field = ProperyColourField(self, name=prop)
            sizer.Add(field, 1, wx.EXPAND)
            egd_msg.sendMessage(egd_msg.EGD_MSG_REG_PROP, data={prop:field})

        # Font Field
        label = wx.StaticText(self, label=_("Font"))
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
        field = PropertyFontField(self, name='Font')
        sizer.Add(field, 1, wx.EXPAND)
        egd_msg.sendMessage(egd_msg.EGD_MSG_REG_PROP, data={'Font':field})

        sizer.AddGrowableCol(1, 1)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        self.SetSizer(hsizer)

#-----------------------------------------------------------------------------#

class PropertyTextField(egdgui.TextEntry):
    def notifyChanged(self):
        egd_msg.sendMessage(egd_msg.EGD_MSG_PROP_CHANGED,
                            data=dict(field=self, value=self.GetValue()))

class ProperyColourField(egdgui.ColourEntry):
    def notifyChanged(self):
        egd_msg.sendMessage(egd_msg.EGD_MSG_PROP_CHANGED,
                            data=dict(field=self, value=self.GetColour()))

class PropertyFontField(egdgui.FontEntry):
    def notifyChanged(self):
        egd_msg.sendMessage(egd_msg.EGD_MSG_PROP_CHANGED,
                            data=dict(field=self, value=self.GetSelectedFont()))

#-----------------------------------------------------------------------------#

#ForegroundColour
#BackgroundColour
#BackgroundStyle

#Border

#Shown
#Enabled

#ExtraStyle
#WindowStyle
#WindowStyleFlag
#WindowVariant
#Font

#HelpText
#ToolTip

#Label
#LabelText

#LayoutDirection
#MaxHeight
#MaxSize
#MaxWidth
#MinHeight
#MinSize
#MinWidth
#Size
#Position
#Rect
#BestSize
#EffectiveMinSize
