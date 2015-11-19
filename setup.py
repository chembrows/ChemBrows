#!/usr/bin/python
# coding: utf-8


import sys
import os
from esky.bdist_esky import Executable
from setuptools import setup


# --------------------------------------------------
# http://blog.gmane.org/gmane.comp.python.cx-freeze.user/month=20140201

# With PyQt5.2 there is a problem in the way that the PyQt modules are built that causes cx_freeze to stop with an error because a .dylib cannot be found.

# If cx_freeze terminates with a message like:

# > FileNotFoundError: [Errno 2] No such file or directory: 'libQtCore.dylib'

# then cd into the location for the PyQt5 modules, probably

# > /Library/Frameworks/Python.framework/Versions/Current/lib/python3.3/site-packages/PyQt5

# and use the otool command to display their depencies, e.g.

# > $ otool -L ./QtCore.so
# > ./QtCore.so:
# >     libQtCore.dylib (compatibility version 0.0.0, current version 0.0.0)
# >     /usr/local/Qt-5.2.0/lib/QtCore.framework/Versions/5/QtCore (compatibility version 5.2.0, current version 5.2.0)
# >     /usr/lib/libstdc++.6.dylib (compatibility version 7.0.0, current version 60.0.0)
# >     /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1197.1.1)

# There is an apparent dependency on libQtCore.dylib but this is an artifact of the way the module was built. This should be corrected in a future release of PyQt5. But for now, apply the following command:

# > $ sudo install_name_tool -id $PWD/QtCore.so QtCore.so

# This has to be done for each module the frozen app imports, QtWidgets, QtWebKit, etc.


# --------------------------------------------------

# http://stackoverflow.com/questions/22728468/osx-pillow-incompatible-library-version-libtiff-5-dylib-libjpeg-8-dylib

# For errors of this kind:
# ImportError: dlopen(/Library/Python/2.7/site-packages/PIL/_imaging.so, 2): Library not loaded: /usr/local/lib/libjpeg.8.dylib
  # Referenced from: /usr/local/lib/libtiff.5.dylib


# --------------------------------------------------

# To correct:
# TypeError: dyld_find() got an unexpected keyword argument 'loader'

# http://stackoverflow.com/questions/31240052/py2app-typeerror-dyld-find-got-an-unexpected-keyword-argument-loader

# Open the file /virtenv/lib/python3.4/site-packages/macholib/dyld.py and replace each instance of loader_path with loader

# --------------------------------------------------

# To solve:

# error: can't copy 'dist/EskyExample-0.0.1.macosx-10_6-intel/EskyExample-0.0.1.macosx-10_6-intel/EskyExample.app/Contents/Resources/lib/python3.3/config': doesn't exist or not a regular file

# /usr/local/lib/python3.4/site-packages/esky/bdist_esky
# ligne 122 modifier config en config-3.4m)

# --------------------------------------------------


# https://github.com/Homebrew/homebrew/issues/11122

# To solve:
# On Mac OS X, you might be loading two sets of Qt binaries into the same process. Check that all plugins are compiled against the right Qt binaries. Export DYLD_PRINT_LIBRARIES=1 and check that only one set of binaries are being loaded.

# AND:

# Database error: Driver not loaded Driver not loaded

# create a qt.conf file in Content/Resources:

# #Provide QT with a bogus path to avoid double loading of libs
# #Needed for QT4.8.0 on OSX 10.7
# [Paths]
# Plugins = Resources/plugins

# And make the following tree:
# Contents/Resources/plugins/sqldrivers/libqsqlite.dylib

# Same thing for imageformats

# --------------------------------------------------

# if the package is bundled with Esky, to produce a simple runnable.app:

# modify dist/ChemBrows-0.8.0.macosx-10_10-x86_64/ChemBrows.app/Contents/Info.plist to get:

    # <key>CFBundleExecutable</key>
    # <string>launcher</string>

# Then create /dist/ChemBrows-0.8.0.macosx-10_10-x86_64/ChemBrows.app/Contents/MacOS/launcher,
# and put that inside:

# #!/usr/bin/env bash
# cd "${0%/*}"
# open ../../ChemBrows-0.8.0.macosx-10_10-x86_64/ChemBrows.app

# Don't forget to chmod +x launcher, and VERY IMPORTANT, rename the .app top folder, and rename it
# back after, otherwise the changes in Info.plist will not count




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
my_data_files += get_all_files_in_dir('.{}images{}'.format(os.path.sep, os.path.sep))
my_data_files += get_all_files_in_dir('.{}journals{}'.format(os.path.sep, os.path.sep))
my_data_files += get_all_files_in_dir('.{}config{}'.format(os.path.sep, os.path.sep))
my_data_files += get_all_files_in_dir('.{}config{}fields{}'.format(os.path.sep, os.path.sep, os.path.sep))
my_data_files += get_all_files_in_dir('.{}config{}styles{}'.format(os.path.sep, os.path.sep, os.path.sep))

# Remove sensitive files
try:
    my_data_files.remove(('.{}config{}'.format(os.path.sep, os.path.sep), ['.{}config{}searches.ini'.format(os.path.sep, os.path.sep)]))
except ValueError:
    pass
try:
    my_data_files.remove(('.{}config{}'.format(os.path.sep, os.path.sep), ['.{}config{}options.ini'.format(os.path.sep, os.path.sep)]))
except ValueError:
    pass
try:
    my_data_files.remove(('.{}config{}'.format(os.path.sep, os.path.sep), ['.{}config{}options.ini_save'.format(os.path.sep, os.path.sep)]))
except ValueError:
    pass
try:
    my_data_files.remove(('.{}config{}'.format(os.path.sep, os.path.sep), ['.{}config{}twitter_credentials'.format(os.path.sep, os.path.sep)]))
except ValueError:
    pass


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform in ['win32', 'cygwin', 'win64']:
    base = "Win32GUI"

    # Copy the sqlite driver
    my_data_files.append(('sqldrivers', ['C:\Python34\Lib\site-packages\PyQt4\plugins\sqldrivers\qsqlite4.dll']))

    FREEZER = 'cx_Freeze'
    FREEZER_OPTIONS = dict()

elif sys.platform == 'darwin':
    FREEZER = 'py2app'
    my_data_files.append(('plugins/sqldrivers', ['/usr/local/Cellar/qt/4.8.7/plugins/sqldrivers/libqsqlite.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqgif.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqico.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqjpeg.dylib']))
    my_data_files.append(('.', ['./deploy/qt.conf']))
    FREEZER_OPTIONS = dict()
else:
    my_data_files.append(('sqldrivers', ['/usr/lib/qt4/plugins/sqldrivers/libqsqlite.so']))
    FREEZER = 'cx_Freeze'
    FREEZER_OPTIONS = dict()

print(my_data_files)

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
           ]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                     'bdist_esky': {
                                    'freezer_module': FREEZER,
                                    'freezer_options': FREEZER_OPTIONS,
                                    'includes': includes,
                                    'excludes': excludes,
                                   },
                     }


exe_esky = Executable("gui.py", gui_only=True)

# Get the current version from the version file
with open('config/version.txt', 'r') as version_file:
    version = version_file.read().rstrip()

setup(name="ChemBrows",
      version=version,
      description="ChemBrows keeps you up-to-date with scientific litterature",
      data_files=my_data_files,
      options=build_exe_options,
      scripts=[exe_esky],
      )
