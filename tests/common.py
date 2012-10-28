###############################################################################
# Name: common.py                                                             #
# Purpose: Unit test tools                                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Common tools for the unittest suite"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision: $"

#-----------------------------------------------------------------------------#
# Imports
import os
import locale
import shutil

#-----------------------------------------------------------------------------#

def cleanTempDir():
    """Clean all files from the temporary directory"""
    tdir = GetTempDir()
    for path in os.listdir(tdir):
        if path.startswith(u'.'):
            continue

        fpath = os.path.join(tdir, path)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)

def getDataDir():
    """Get the path to the test data directory
    @return: string

    """
    path = os.path.join(u'.', u'data')
    return os.path.abspath(path)

def getDataFilePath(fname):
    """Get the absolute path of the given data file
    @param fname: filename
    @return: string

    """
    path = os.path.join(u'.', u'data', fname)
    return os.path.abspath(path)

def getFileContents(path):
    """Get the contents of the given file
    @param path: string
    @return: string

    """
    handle = open(path, 'rb')
    txt = handle.read()
    handle.close()
    return txt

def getDataFileContents(fname):
    """Get the contents of a file in the data directory
    @param fname: file name
    @return: string

    """
    path = getDataFilePath(fname)
    xmlstr = getFileContents(path)
    return xmlstr

def getTempDir():
    """Get the path to the test temp directory
    @return: string

    """
    path = os.path.join(u'.', u'temp')
    return os.path.abspath(path)

def getTempFilePath(fname):
    """Get a path for a file in the temp directory
    @param fname: File name to get path for
    @return: string

    """
    tdir = getTempDir()
    return os.path.join(tdir, fname)

def makeTempFile(fname):
    """Make a new file in the temp directory with a give name
    @param fname: file name
    @return: new file path

    """
    path = os.path.join(getTempDir(), fname)
    if not os.path.exists(path):
        handle = open(path, "wb")
        handle.write(" ")
        handle.close()
    return path

