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
__all__ = ['ControlStrategy',]

#-----------------------------------------------------------------------------#
# Imports
import wx

import _objectxml

#-----------------------------------------------------------------------------#

class WrapperPanel(wx.Panel):
    """Helper class for creating designer controls
    Wraps the given control class within an instance of this
    panel class.

    """
    def __init__(self, parent, ctor, *args, **kwargs):
        super(WrapperPanel, self).__init__(parent)

        self._control = ctor(self, *args, **kwargs)

        # Layout
        sizer = wx.BoxSizer()
        sizer.Add(self._control, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()

    Control = property(lambda self: self._control)

#-----------------------------------------------------------------------------#

class ControlStrategy(object):
    """Defines an interface for L{DesignerControl} construction
    and properties strategies. This class defines and provides an 
    implementation that is works for most common controls.

    Controls with more special needs should derive from this class
    and override the necessary methods to provide the customized
    strategy for creating the control for the designer.

    """
    def __init__(self, name):
        super(ControlStrategy, self).__init__()

        # Attributes
        self.name = name

    @classmethod
    def factoryCreate(cls, name, module, argspec):
        for strategy in cls.__subclasses__():
            if strategy.isStrategyFor(name, module, argspec):
                return strategy(name)
            else:
                # Recursively check for subclasses of subclasses
                obj = strategy.factoryCreate(name, module, argspec)
                if type(obj) == ControlStrategy:
                    # Keep trying
                    continue
                else:
                    return obj
        else:
            return ControlStrategy(name)

    #---- Implementation ----#

    def construct(self, ctor, parent):
        """Called by client code to construct the object"""
        obj = None
        try:
            obj = self.initInstance(ctor, parent)
        except Exception, msg:
            # TODO: add proper logging facilities
            print "Failed construct", msg
        else:
            self.postInitSetup(obj)
        return obj

    def getXml(self, obj):
        """Get the xml representation of this object
        @param obj: Designer Control

        """
        xmlobj = _objectxml.EgdObject()
        xmlobj.name = obj.Instance.Name
        xmlobj.properties = getPropertiesXml(obj.Instance)
        self.serialize(obj, xmlobj)
        return xmlobj

    #---- Must override in subclasses ----#

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        """Check if this strategy can handle the given control
        @param name: Control class name
        @param module: module control will be loaded from
        @param argspec: ArgSpec object
        @return: bool

        """
        raise NotImplementedError("Must implement isStrategyFor!")

    #---- Optionally override in subclasses ----#

    def initInstance(self, ctor, parent=None):
        """Create an instance of the class object
        @param ctor: class constructor function
        @keyword parent: parent window the control belongs to
        @return: control instance

        """
        return ctor(parent, *self.getArgs(), **self.getKWArgs())

    def getArgs(self):
        """Get an order list of arguments for the ctor"""
        return [wx.ID_ANY,]

    def getKWArgs(self):
        """Get the keyword arguments for the ctor"""
        return dict()

    def postInitSetup(self, control):
        """Do any setup steps on a control instance
        @param control: wx.Window Instance

        """
        pass

    def serialize(self, ctrl, exml):
        """Add any non standard attributes to the xml object to
        allow for the control to be properly serialized in the
        project.
        @param ctrl: wxWindow instance
        @param exml: EgdObject xml instance to add (out param)
        @return: None

        """
        pass

#-----------------------------------------------------------------------------#
# Utilities

def getPropertiesXml(obj):
    """Get a list of EgdProperty objects from the Window object
    @param obj: Window instance
    @return: list of EgdProperty objects

    """
    proplist = list()
    for attr in dir(obj.__class__):
        attrinst = getattr(obj.__class__, attr)
        if type(attrinst) is property:
            prop = _objectxml.EgdProperty()
            prop.name = attr
            prop.value = getattr(obj, attr) # Get the actual value
            proplist.append(prop)
    return proplist

#-----------------------------------------------------------------------------#
# Common Strategy Base Classes

class ControlWithLabelStrategy(ControlStrategy):
    """Construction strategy for control that has a label
    keyword parameter.

    """
    def __init__(self, name):
        super(ControlWithLabelStrategy, self).__init__(name)

    def getKWArgs(self):
        return dict(label=self.name)

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        # Core wx controls often just have *args, **kwargs arguments
        # from wrapper code so need to check the name specifically.
        bCanHandle = name in ('Button', 'CheckBox',
                              'RadioButton', 'StaticText', 'ToggleButton')
        if not bCanHandle:
            # Check args specifically
            bCanHandle = 'label' in argspec[0]
        return bCanHandle

class ControlWithChoicesStrategy(ControlStrategy):
    """Construction strategy for control that has a choices
    keyword parameter.

    """
    def __init__(self, name):
        super(ControlWithChoicesStrategy, self).__init__(name)

    def getKWArgs(self):
        return dict(choices=["Choice %d" % item for item in range(3)])

    @classmethod
    def isStrategyFor(cls, name, module, argspec):
        # Core wx controls often just have *args, **kwargs arguments
        # from wrapper code so need to check the name specifically.
        bCanHandle = name in ('Choice', 'CheckListBox', 'ListBox')
        if not bCanHandle:
            # Check args specifically
            bCanHandle = 'choices' in argspec[0]
        return bCanHandle
