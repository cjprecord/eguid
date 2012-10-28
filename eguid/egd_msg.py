# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_msg.py                                                            #
# Purpose: Message callback passing interface                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Acts as a simple wrapper around pubsub module

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
from extern.pubsub import Publisher

#-----------------------------------------------------------------------------#

def subscribe(callback, topic):
    Publisher().subscribe(callback, topic)

def sendMessage(topic, data=None):
    Publisher().sendMessage(topic, data, context=None)

def unsubscribe(callback, messages=None):
    Publisher().unsubscribe(callback, messages)

#-----------------------------------------------------------------------------#
# Message Topics

# Root message
EGD_MSG_ROOT = 'egdroot'

# Inspector Dialog Messages
EGD_MSG_INSPECTOR = EGD_MSG_ROOT + '.inspector'
# data == dict(PropName=field,)
EGD_MSG_REG_PROP = EGD_MSG_INSPECTOR + '.regproperty'
# data == dict(field=ctrl, value=new_property_value)
EGD_MSG_PROP_CHANGED = EGD_MSG_INSPECTOR + '.propertychanged'

# Designer Messages
EGD_MSG_DESIGNER = EGD_MSG_ROOT + '.designer'
# data == DesignerWindow (top level designer container)
EGD_MSG_DESIGNER_NEW_WINDOW = EGD_MSG_DESIGNER + '.newdesigner'
# data == DesignerControl
EGD_MSG_DESIGNER_FOCUS_CHANGED = EGD_MSG_DESIGNER + '.focuschanged'
# Designer control was instantiated
# data == DesignerControl
EGD_MSG_DESIGNER_CTRL_CREATED = EGD_MSG_DESIGNER + '.ctrlcreated'
# Designer control was added to a designer window
# data == DesignerControl
EGD_MSG_DESIGNER_CTRL_ADDED = EGD_MSG_DESIGNER + '.ctrladded'
# data == DesignerControl
EGD_MSG_DESIGNER_CTRL_DELETED = EGD_MSG_DESIGNER + '.ctrldeleted'

# Library Loader
EGD_MSG_LOADER = EGD_MSG_ROOT + '.loader'
# data == None
EGD_MSG_LOADER_START = EGD_MSG_LOADER + ".start"
EGD_MSG_LOADER_END = EGD_MSG_LOADER + ".end"
# data == status string
EGD_MSG_LOADER_STATUS = EGD_MSG_LOADER + '.statusupdate'

