# -*- coding: utf-8 -*-
###############################################################################
# Name: egd_libloader.py                                                      #
# Purpose: Designer Library Loader                                            #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Library manager for loading control libraries for the Designer

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import threading
import wx

# Local imports
import egd_cfg
import egd_msg
import egdbm
from egd_designerctrl import DesignerControl

#-----------------------------------------------------------------------------#

class LibraryLoader(object):
    """Load and generate designer control libraries"""
    def __init__(self):
        super(LibraryLoader, self).__init__()

        # Attributes
        self._libs = dict()
        self.loading = None

    library = property(lambda self: self._libs)

    def isLoading(self):
        loading = False
        if self.loading:
            loading = self.loading.isAlive()
        if not loading:
            self.loading = None
        return loading

    def loadDefault(self):
        """Load the default libraries"""
        libs = [Loader('wx', loadWXCore),
                Loader('wx.lib', loadWXLib),
                Loader('wx.lib.agw', loadPackage)]
        self.loading = LoaderThread(libs,
                                    self.updateStatus,
                                    self.updateLibrary)
        self.loading.start()
        egd_msg.sendMessage(egd_msg.EGD_MSG_LOADER_START)

    def updateStatus(self, status):
        wx.CallAfter(egd_msg.sendMessage, egd_msg.EGD_MSG_LOADER_STATUS, status)

    def updateLibrary(self, loader):
        # TODO: add lock around modification of _libs
        self._libs[loader.name] = loader.library

#-----------------------------------------------------------------------------#

class LoaderThread(threading.Thread):
    def __init__(self, loaders, status, target, force=False):
        """Loads a list of libraries into memory
        @param loaders: list of loader objects
        @param status: callable to get status updates funct(str)
        @param target: callable to receive lib funct(loader)
        @keyword force: force a regen of the library regardless of cached version

        """
        assert callable(status), "status must be callable!"
        assert callable(target), "target must be callable!"
        super(LoaderThread, self).__init__()

        # Attributes
        self._loaders = loaders
        self._status = status
        self._target = target
        self._force = force
        self._remaining = len(loaders)

    remaining = property(lambda self: self._remaining)

    def run(self):
        cfg = egd_cfg.EgdConfig()
        libdir = cfg.libraryDir
        for lib in self._loaders:
            loaded = list()
            # TODO handle localization... GetTranslation is not thread safe
            self._status(u"Loading %s..." % lib.name)
            # Check if we have already generated the xml
            if not self._force:
                loaded = self.loadFromXml(lib)
                if len(loaded):
                    self._status(u"Loaded %s from library file" % lib.name)
                    lib.library = loaded
                    self._remaining -= 1
                    self._target(lib)
                    continue
            # Load from module/package by introspection
            lib.doLoad()
            self._status(u"Loaded %s" % lib.name)
            self._remaining -= 1
            self._target(lib)
            self._status(u"Serializing %s" % lib.name)
            libxml = egdbm.EgdLibrary()
            libxml.name = lib.name
            # TODO: HACK
            if lib.name.startswith("wx"):
                cversion = wx.__version__
            else:
                cversion = getattr(lib.module, '__version__', None)
            libxml.version = cversion
            for ctrl in lib.library:
                ctrlxml = egdbm.EgdControl()
                ctrlxml.name = ctrl.Name
                ctrlxml.module = ctrl.Module.__name__
                libxml.controls.append(ctrlxml)
            libxml.write(os.path.join(libdir, "%s.elib" % lib.name))

        # Notify loading completed
        wx.CallAfter(egd_msg.sendMessage, egd_msg.EGD_MSG_LOADER_END)

    def loadFromXml(self, loader):
        """Load a library from xml cache
        @param loader: Loader object
        @return: list

        """
        loaded = list()
        cfg = egd_cfg.EgdConfig()
        libdir = cfg.libraryDir
        libname = "%s.elib" % loader.name
        path = os.path.join(libdir, libname)
        if os.path.exists(path):
            libxml = egdbm.EgdLibrary.load(path)
            version = libxml.version
            if libxml and version:
                # Check version against current lib version
                mod = getModule(loader.name)
                # TODO: HACK
                if loader.name.startswith("wx"):
                    cversion = wx.__version__
                else:
                    cversion = getattr(mod, '__version__', None)

                if cversion == version:
                    # Can load from xml
                    for ctrl in libxml.controls:
                        mod = getModule(ctrl.module)
                        loaded.append(DesignerControl(ctrl.name, mod))
        return loaded

#-----------------------------------------------------------------------------#

class Loader(object):
    """Loader Object"""
    def __init__(self, name, loader):
        """Loader object
        @param name: module/package name (importable name)
        @param loader: callable

        """
        super(Loader, self).__init__()

        # Attributes
        self._name = name
        self._loader = loader
        self._lib = list()

    name = property(lambda self: self._name,
                    lambda x, v: setattr(self, '_name', v))
    library = property(lambda self: self._lib,
                       lambda self, v: setattr(self, '_lib', v))
    module = property(lambda self: getModule(self._name))

    def doLoad(self):
        """Load the library/package"""
        ctrls = self._loader(self.name)
        ctrls.sort(key=lambda x: x.Name)
        self._lib = ctrls

#-----------------------------------------------------------------------------#

def loadWXCore(package):
    library = dict()

    # Load wx core library
    controls = introspectModule(wx)
    controls.append(DesignerControl('StatusBar', wx))
    controls.append(DesignerControl('MenuBar', wx))
    # Remove 'Base' classes as they are not to be used directly
    remove = [idx for idx, dobj in enumerate(controls)
              if dobj.Name.endswith('Base')]
    remove.reverse()
    for idx in remove:
        del controls[idx]
    # Filter out other known controls that should be excluded
    remove = [ idx for idx, dobj in enumerate(controls)
               if dobj.Name in ('Control', 'PyControl',
                                'ControlWithItems', 'ListView')]
    remove.reverse()
    for idx in remove:
        del controls[idx]
    return controls

def loadWXLib(package):
    excludes = ["wxPlotCanvas.py", "rightalign.py", "pyshell.py",
                "mvctree.py", "grids.py", "floatbar.py", "shell.py",
                "splashscreen.py"]
    ctrls = loadPackage("wx.lib", excludes)
    return ctrls

def getModule(name):
    """Get the module by name
    @return: module or None

    """
    mod = None
    try:
        if '.' in name:
            mod = getDottedModule(name)
        else:
            mod = __import__(name)
    except:
        pass
    return mod

def getDottedModule(name):
    mod = None
    try:
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
    except:
        pass
    return mod

def loadPackage(package, excludes=list()):
    """Generate control list of all controls from all
    modules inside the given package.

    """
    controls = list()
    try:
        pkg = getDottedModule(package)
        path = os.path.dirname(pkg.__file__)
        for module in os.listdir(path):
            if module.endswith('.py'):
                if module in excludes:
                    continue
                mname = module.rsplit('.py', 1)[0]
                try:
                    mod = getDottedModule("%s.%s" % (package, mname))
                    tmp = introspectModule(mod)
                    controls.extend(tmp)
                except Exception:
                    pass
    except ImportError:
        pass
    return controls

def introspectModule(module):
    """Try to find all controls in a module
    @return: list of DesignerControls

    """
    controls = list()
    for obj in dir(module):
        attr = getattr(module, obj)
        otype = type(attr)
        if otype is type:
            if issubclass(attr, wx.Control) or issubclass(attr, wx.PyControl):
                dcontrol = DesignerControl(obj, module)
                controls.append(dcontrol)
    return controls
