# -*- coding: utf-8 -*-
###############################################################################
# Name: _fileutil.py                                                          #
# Purpose: File Utilities                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Filesystem utilities

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['makeDirectory',]

#-----------------------------------------------------------------------------#
# Imports
import os
import sys

#-----------------------------------------------------------------------------#

def makeDirectory(path):
    """Make a directory at the given path
    @param path: directory path
    @return success: bool

    """
    bOk = True
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            bOk = False
    return bOk
