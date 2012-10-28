# -*- coding: utf-8 -*-
###############################################################################
# Name: edg_cfg.py                                                            #
# Purpose: Eguid Configuration                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import egdbm
import egd_util

#-----------------------------------------------------------------------------#

class EgdConfig(egdbm.ConfigurationBase):
    __metaclass__ = egd_util.Singleton
    def __init__(self):
        super(EgdConfig, self).__init__()

    # Properties
    configDir = property(lambda self: self.getUserConfigDir())
    libraryDir = property(lambda self: self.getUserConfigDir("library"))

