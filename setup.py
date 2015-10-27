#!/usr/bin/python
# coding: utf-8


import sys
import os
import esky.bdist_esky
from esky.bdist_esky import Executable as Executable_Esky
from cx_Freeze import setup, Executable




def get_all_files_in_dir(directory):

    """Get all the files in a directory, and
    return a list bdist formatted"""

    list_files = []

    for file in os.listdir(directory):
        f1 = directory + file
        if os.path.isfile(f1):  # skip directories
            f2 = (directory, [f1])
            list_files.append(f2)

    return list_files


my_data_files = []

# Add the data in images, journals, and config
my_data_files += get_all_files_in_dir('.{}images{}'.format(os.sep, os.sep))
my_data_files += get_all_files_in_dir('.{}journals{}'.format(os.sep, os.sep))
my_data_files += get_all_files_in_dir('.{}config{}'.format(os.sep, os.sep))
my_data_files += get_all_files_in_dir('.{}config{}fields{}'.format(os.sep, os.sep, os.sep))
my_data_files += get_all_files_in_dir('.{}config{}styles{}'.format(os.sep, os.sep, os.sep))

# Remove sensitive files
my_data_files.remove(('./config/', ['./config/searches.ini']))
my_data_files.remove(('./config/', ['./config/options.ini']))
my_data_files.remove(('./config/', ['./config/twitter_credentials']))

# import scipy
# scipy_path = os.path.dirname(scipy.__file__)
# includefiles = [scipy_path]
# print(includefiles)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform in ['win32', 'cygwin', 'win64']:
    base = "Win32GUI"

    # Copy the sqlite driver
    my_data_files.append(('sqldrivers', ['C:\Python34\Lib\site-packages\PyQt4\plugins\sqldrivers/qsqlite4.dll']))

    # # Copy the plugins to load images
    # my_data_files.append('C:\Python34\Lib\site-packages\PyQt4\plugins\imageformats\\')

elif sys.platform == 'darwin':
    pass
else:
    my_data_files.append(('sqldrivers', ['/usr/lib/qt4/plugins/sqldrivers/libqsqlite.so']))


excludes = [
            # Personal modules
            'test_hosts',
            'test_worker',
            'misc',

            # 'tkinter',
            # 'certifi',
            # 'cffi',
            # 'cryptography',
            # 'curses',
            # 'gi',
            # 'IPython'
            # 'json'
            # 'jsonschema',
            # 'lib2to3',
            # 'nose',
            # 'OpenSSL',
            # 'pkg_resources',
            # 'psutil',
            # 'pyasn1',
            # 'pycparser',
            # 'pydoc_data',
            # 'PyQt5',
            # 'pytz',
            # 'tornado',
            # 'zmq',
            # 'lxml',
            # 'matplotlib',
            # 'html5lib',
            # 'xml',
            # 'xmlrpc',
            # 'decimal',
            # 'doctest',
            # 'configparser',
            # 'ftplib',
            # 'smtplib',
            # 'ssl',
            # 'fractions',
            # 'site',
            # 'termios',
            # 'tty',
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
            'lxml',
            'gzip',
           ]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                     # 'build_exe': {
                                   # 'include_files': includefiles,
                                  # },
                     'bdist_esky': {
                                    'freezer_module': 'cx_Freeze',
                                    'includes': includes,
                                    'excludes': excludes,
                                   },
                     }


exe_esky = Executable_Esky("gui.py", gui_only=True)
exe_cx = Executable(script="gui.py", base=base, compress=False)

# Get the current version from the version file
with open('config/version.txt', 'r') as version_file:
    version = version_file.read()

setup(name="ChemBrows",
      version=version,
      description="ChemBrows keeps you up-to-date with scientific litterature",
      data_files=my_data_files,
      options=build_exe_options,
      scripts=[exe_esky],
      executables=[exe_cx],
      )
