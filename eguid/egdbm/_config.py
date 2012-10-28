# -*- coding: utf-8 -*-
###############################################################################
# Name: _config.py                                                            #
# Purpose: Configuration utility classes                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Configuration management class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"
__all__ = ['ConfigurationBase',]

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Local Imports
import _fileutil

#-----------------------------------------------------------------------------#

class ConfigurationBase(object):
    """Configuration management base class"""
    def __init__(self):
        super(ConfigurationBase, self).__init__()

        # Attributes
        self._stdpaths = wx.StandardPaths.Get()

    def getUserConfigDir(self, subdir=None):
        """Get the users data directory for storing configuration data.
        @keyword subdir: get a subdirectory path

        """
        path = self._stdpaths.GetUserConfigDir()
        path = os.path.join(path, wx.GetApp().GetAppName())
        if not os.path.exists(path):
            _fileutil.makeDirectory(path)
        if subdir is not None:
            assert isinstance(subdir, basestring), "subdir must be a string!"
            path = os.path.join(path, subdir)
        return path

    def hasConfigDir(self, dname):
        """Does the configuration subdirectory exist?
        @param dname: configuration directory
        @return: bool

        """
        path = self.getUserConfigDir()
        path = os.path.join(path, dname)
        return os.path.exists(path)

    def makeConfigDir(self, dname):
        """Make a configuration subdirectory
        @param dname: directory name
        @return: bool (was it created?)

        """
        assert isinstance(dname, basestring), "dname must be a string!"
        bCreated = True
        path = self.getUserConfigDir()
        path = os.path.join(path, dname)
        if not os.path.exists(path):
            bCreated = _fileutil.makeDirectory(path)
        return bCreated
