# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Editra Gui Designer Business Model                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Eguid Business Model

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#

# Import namespaces
# XML Classes
from _basexml import *
from _projectxml import *
from _objectxml import *
from _libraryxml import *

# Utility Classes
from _fileutil import *
from _config import *

# Import some items from dexml for more convenient access
from dexml import Error, ParseError, RenderError, XmlError

# Import control strategy
from controlstrategy import ControlStrategy, getPropertiesXml

#-----------------------------------------------------------------------------#
# Initialize factory classes
def initStrategyFactory():
    import os
    for mod in os.listdir(os.path.dirname(__file__)):
        if mod.startswith('_') and not mod.startswith('__'):
            if mod.endswith('strategy.py'):
                modname = mod.rsplit('.', 1)[0]
                try:
                    mod = __import__(modname, globals())
                except ImportError, msg:
                    # TODO: Proper logging of errors
                    print "initStrategyFactory FAIL", msg
initStrategyFactory()
del initStrategyFactory
