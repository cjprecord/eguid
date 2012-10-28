# -*- coding: utf-8 -*-
###############################################################################
# Name: egd_designerctrl.py                                                   #
# Purpose: Designer Control Manager Class                                     #
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
import inspect
import types

# Local Imports
from egdbm import ControlStrategy
import egd_ids
import IconResource
import egd_msg

#-----------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class DesignerControl(object):
    def __init__(self, name, namespace):
        """Represents a control within the designer view
        @param name: class name
        @param namespace: module class is found in

        """
        assert isinstance(name, basestring)
        assert type(namespace) is types.ModuleType
        super(DesignerControl, self).__init__()

        # Attributes
        self._name = name
        self._namespace = namespace
        self._instance = None
        self.strategy = None
        self._moving = False

    # Properties
    Constructor = property(lambda self: getattr(self.Module, self.Name, None))
    Instance = property(lambda self: self._instance,
                        lambda self, obj: setattr(self, '_instance', obj))
    Name = property(lambda self: self._name,
                    lambda self, name: setattr(self, '_name', name))
    Module = property(lambda self: self._namespace)
    AnchorPoints = property(lambda self: self.getAnchorPoints())
    Rect = property(lambda self: wx.Rect(*self.Instance.Rect).Inflate(3, 3))
    Moving = property(lambda self: self._moving,
                      lambda self, moving: setattr(self, '_moving', moving))

    #---- Accessors ----#

    def clone(self):
        return DesignerControl(self.Name, self.Module)

    def createInstance(self, parent):
        """This should be called prior to using anything outside of the
        controls Name to create an instance of the control in the designer.

        """
        if not self.Instance:
            obj = None
            try:
                argspec = inspect.getargspec(self.Constructor.__init__)
                self.strategy = ControlStrategy.factoryCreate(self.Name,
                                                              self.Module,
                                                              argspec)
                obj = self.strategy.construct(self.Constructor, parent)
                # TODO: Set Name property to be unique for all siblings
                #       on a given window.
                obj = objectWrap(self, obj) # TODO: should be done by strategy?
            except Exception, msg:
                # TODO: proper logging facilities
                print "ERROR", msg
            self.Instance = obj
            # Notify observers that a new designer control was created
            if self.Instance:
                egd_msg.sendMessage(egd_msg.EGD_MSG_DESIGNER_CTRL_CREATED, self)

    def doDrawDecorations(self, dc):
        """Draw the bounding box and other decorations around the
        control.
        @param dc: Device Context to draw on (owned by parent)

        """
        assert self.Instance, "Control not created yet!"

        gc = wx.GCDC(dc)
        # Draw a bounding box around the control
        pen = wx.Pen(wx.BLUE, 1)
        gc.SetPen(pen)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawRectangleRect(self.Rect)

        # Draw the anchor points
        gc.SetBrush(wx.BLUE_BRUSH)
        points = self.AnchorPoints
        for point in points.values():
            gc.DrawCirclePoint(point, 2)

        # Draw Alignment Lines
        if self.Moving:
            pen = wx.Pen(wx.BLUE, 1, wx.DOT)
            pen.SetCap(wx.CAP_ROUND)
            gc.SetPen(pen)
            rect = self.Instance.Parent.ClientRect

            # Draw Left Line
            left = points['LeftMiddle']
            left = left + (rect.x, left[1])
            gc.DrawLine(*left)
            lx = left[0] - left[2]
            lxlbl = "%dpx" % lx
            txt_w, txt_h = gc.GetTextExtent(lxlbl)
            lblrect = wx.Rect(rect.x, left[1] - txt_h, left[0], txt_h)
            gc.DrawLabel(lxlbl, lblrect, wx.ALIGN_CENTER)

            # Draw Right Line
            right = points['RightMiddle']
            right = right + (rect.x + rect.width, left[1])
            gc.DrawLine(*right)
            rx = right[2] - right[0]
            rxlbl = "%dpx" % rx
            txt_w, txt_h = gc.GetTextExtent(rxlbl)
            lblrect = wx.Rect(right[0], right[1] - txt_h, rx, txt_h)
            gc.DrawLabel(rxlbl, lblrect, wx.ALIGN_CENTER)

            # Draw Top Line
            top = points['TopMiddle']
            top = top + (top[0], rect.y)
            gc.DrawLine(*top)
            tx = top[1] - top[3]
            txlbl = "%dpx" % tx
            txt_w, txt_h = gc.GetTextExtent(txlbl)
            lblrect = wx.Rect(top[0], rect.y, txt_w, tx)
            gc.DrawLabel(txlbl, lblrect, wx.ALIGN_CENTER_VERTICAL)

            # Draw Bottom Line
            bottom = points['BottomMiddle']
            bottom = bottom + (bottom[0], rect.y + rect.height)
            gc.DrawLine(*bottom)
            bx = bottom[3] - bottom[1]
            bxlbl = "%dpx" % bx
            txt_w, txt_h = gc.GetTextExtent(bxlbl)
            lblrect = wx.Rect(bottom[0], bottom[1], txt_w, bx)
            gc.DrawLabel(bxlbl, lblrect, wx.ALIGN_CENTER_VERTICAL)

    def getAnchorPoints(self):
        """Get a mapping of client points of where the bounding boxes
        anchor points are located.
        @return: dict(TopLeft,TopRight,TopMiddle,BottomLeft,
                      BottomRight,BottomMiddle,LeftMiddle,
                      RightMiddle)
        """
        rect = self.Rect
        points = dict(TopLeft=rect.TopLeft,
                      TopRight=rect.TopRight,
                      TopMiddle=(rect.x + rect.width/2, rect.y),
                      BottomLeft=rect.BottomLeft,
                      BottomRight=rect.BottomRight,
                      BottomMiddle=(rect.x + rect.width/2, rect.y + rect.height),
                      LeftMiddle=(rect.x, rect.y + (rect.height/2)),
                      RightMiddle=(rect.x + rect.width, rect.y + (rect.height/2)))
        return points

    def getCursor(self, point):
        """Get the appropriate cursor for the given point on the
        anchor box.
        @param point: (x,y) (in client coords)

        """
        rect = wx.Rect(*self.Rect).Inflate(2, 2)
        cursor = wx.NullCursor
        if rect.Contains(point):
            brect = self.Rect
            # Check if the point is on a corner
            corners = [ wx.Rect(r.x-2, r.y-2, 4, 4)
                        for r in (brect.TopLeft, brect.TopRight,
                                  brect.BottomLeft, brect.BottomRight) ]
            for idx,corner in enumerate(corners):
                if corner.Contains(point):
                    if idx in (0, 3):
                        cursor = wx.CURSOR_SIZENWSE
                    else:
                        cursor = wx.CURSOR_SIZENESW
                    break
            else:
                # Must be on an edge
                sides = [ wx.Rect(rect.x, rect.y, 4, rect.height),
                          wx.Rect(rect.x+(rect.width-4), rect.y, 4, rect.height),
                          # Top Bottom
                          wx.Rect(rect.x, rect.y, rect.width, 4),
                          wx.Rect(rect.x, rect.y+(rect.height-4), rect.width, 4)]
                for idx,side in enumerate(sides):
                    if side.Contains(point):
                        if idx < 2:
                            cursor = wx.CURSOR_SIZEWE
                        else:
                            cursor = wx.CURSOR_SIZENS

            if cursor != wx.NullCursor:
                cursor = wx.StockCursor(cursor)

        return cursor

    def getXml(self):
        """Get the EgdXml object 
        @return: EgdXml instance

        """
        assert self.Instance, "Control not created yet!"
        xmlobj = self.strategy.getXml(self)
        return xmlobj

#-----------------------------------------------------------------------------#

def objectWrap(dctrl, instance):
    """Augment a control instance to work within the designer
    @param dctrl: DesignerControl
    @param instance: wxWindow instance
    """
    setattr(instance, 'isCurrent', False)
    setattr(instance, 'leftDPos', (0,0))
    setattr(instance, 'leftIsDown', False)
    def setCurrent():
        curr = instance.Parent.getCurrent()
        if curr != instance:
            instance.Parent.clearCurrent()
            instance.isCurrent = True
            instance.Parent.Refresh()
    def onLeftDown(event):
        instance.leftDPos = event.GetPosition()
        instance.leftIsDown = True
        setCurrent()
        event.Skip()
    def onLeftUp(event):
        instance.leftDPos = (0,0)
        instance.leftIsDown = False
        dctrl.Moving = False
        instance.Parent.Refresh()
        event.Skip()
    def onEnter(event):
        instance.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
        event.Skip()
    def onLeave(event):
        instance.SetCursor(wx.NullCursor)
        event.Skip()
    def onMouseMotion(event):
        pos = event.GetPosition()
        if event.LeftIsDown() and instance.leftIsDown:
            dctrl.Moving = True
            dpos = instance.leftDPos
            npos = pos - dpos
            cpos = instance.GetPosition()
            cpos = cpos + npos
            instance.Move(cpos)
            instance.Parent.Refresh()
        event.Skip()
    def onContextMenu(event):
        menu = getattr(instance, '_designer_menu', None)
        if menu:
            menu.Destroy()
            setattr(instance, '_designer_menu', None)
        menu = wx.Menu()
        item = wx.MenuItem(menu, egd_ids.ID_INSPECTOR, _("Inspect"))
        item.Bitmap = IconResource.Inspector16.Bitmap
        menu.AppendItem(item)
        menu.AppendSeparator()
        menu.Append(wx.ID_DELETE, _("Delete"))
        instance._designer_menu = menu
        instance.PopupMenu(menu)
    def bindChildren(event, handler):
        """Glue all children of composite controls together"""
        for child in instance.GetChildren():
            child.Bind(event, handler)
    setattr(instance, 'setCurrent', setCurrent)
    setattr(instance, 'onLeftDown', onLeftDown)
    instance.Bind(wx.EVT_LEFT_DOWN, instance.onLeftDown)
    bindChildren(wx.EVT_LEFT_DOWN, instance.onLeftDown)
    setattr(instance, 'onLeftUp', onLeftUp)
    instance.Bind(wx.EVT_LEFT_UP, instance.onLeftUp)
    bindChildren(wx.EVT_LEFT_UP, instance.onLeftUp)
    setattr(instance, 'onEnter', onEnter)
    instance.Bind(wx.EVT_ENTER_WINDOW, instance.onEnter)
    bindChildren(wx.EVT_ENTER_WINDOW, instance.onEnter)
    setattr(instance, 'onLeave', onLeave)
    instance.Bind(wx.EVT_LEAVE_WINDOW, instance.onLeave)
    bindChildren(wx.EVT_LEAVE_WINDOW, instance.onLeave)
    setattr(instance, 'onMouseMotion', onMouseMotion)
    instance.Bind(wx.EVT_MOTION, instance.onMouseMotion)
    bindChildren(wx.EVT_MOTION, instance.onMouseMotion)
    setattr(instance, 'onContextMenu', onContextMenu)
    instance.Bind(wx.EVT_CONTEXT_MENU, instance.onContextMenu)
    bindChildren(wx.EVT_CONTEXT_MENU, instance.onContextMenu)
    return instance
