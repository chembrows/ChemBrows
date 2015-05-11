#!/usr/bin/python
# coding: utf-8


import sys
import os
from cx_Freeze import setup, Executable


my_data_files = ["./images/", "./journals/", "./config/", "./graphical_abstracts"]

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

    # Copy the sqlite driver
    my_data_files.append(('C:\Python34\Lib\site-packages\PyQt4\plugins\sqldrivers', "sqldrivers"))

    # Copy the plugins to load images
    my_data_files.append('C:\Python34\Lib\site-packages\PyQt4\plugins\imageformats\\')
elif sys.platform=='darwin':
    pass
else:
    my_data_files.append(("/usr/lib/qt4/plugins/sqldrivers", "sqldrivers"))

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"],
                     "excludes": [
                                  "tkinter"
                                 ],
                     'includes': [
                                  'sip',
                                  'PyQt4.QtCore',
                                  'PyQt4.QtGui',
                                  'PyQt4.QtNetwork',
                                  'PyQt4.QtSql',
                                  'scipy.special.specfun',
                                  'scipy.integrate.vode',
                                  'scipy.integrate.lsoda',
                                  'scipy.sparse.csgraph._validation',
                                  'sklearn.utils.sparsetools._graph_validation',
                                  'scipy.special._ufuncs_cxx'
                                 ],
                     'include_files': my_data_files
                    }


setup(name = "guifoo",
      version = "0.1",
      description = "My GUI application!",
      options = {"build_exe": build_exe_options},
      executables = [Executable("gui.py", base=base)])
