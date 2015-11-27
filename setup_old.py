#!/usr/bin/python
# coding: utf-8


import sys, os
from cx_Freeze import setup, Executable

my_data_files = []

my_data_files += ['.{}images{}'.format(os.path.sep, os.path.sep)]
my_data_files += ['.{}journals{}'.format(os.path.sep, os.path.sep)]
my_data_files += ['.{}config{}'.format(os.path.sep, os.path.sep)]
my_data_files += ['.{}config{}fields{}'.format(os.path.sep, os.path.sep, os.path.sep)]

base = None
if sys.platform in ['win32', 'cygwin', 'win64']:
    base = "Win32GUI"
    my_data_files.append(('C:\Python34\Lib\site-packages\PyQt4\plugins\sqldrivers\qsqlite4.dll', 'sqldrivers\qsqlite4.dll'))
elif sys.platform == 'darwin':
    pass
else:
    my_data_files.append(('/usr/lib/qt4/plugins/sqldrivers/libqsqlite.so', 'sqldrivers/libqsqlite.so'))


excludes = [
            'test_hosts',
            'test_worker',
            'misc',
           ]

includes = [
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
            'scipy.special._ufuncs_cxx',
           ]

options = {
           "includes": includes,
           "excludes": excludes,
           "include_files": my_data_files,
           }

exe = Executable("gui.py", base=base)

setup(
    name="monprogramme",
    version="1.00",
    description="monprogramme",
    options={"build_exe": options},
    executables=[exe]
    )
