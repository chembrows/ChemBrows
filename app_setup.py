#!/usr/bin/python
# coding: utf-8


from setuptools import setup
import os, sys

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


if sys.platform in ['win32', 'cygwin', 'win64']:
    pass
elif sys.platform == 'darwin':
    my_data_files.append(('plugins/sqldrivers', ['/usr/local/Cellar/qt/4.8.7/plugins/sqldrivers/libqsqlite.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqgif.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqico.dylib']))
    my_data_files.append(('plugins/imageformats', ['/usr/local/Cellar/qt/4.8.7/plugins/imageformats/libqjpeg.dylib']))
    my_data_files.append('./deploy/qt.conf')
else:
    pass


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
           "argv_emulation": True,
           "includes": includes,
           "excludes": excludes,
           }

exe = ["gui.py"]

setup(
    app = exe,
    name="monprogramme",
    data_files=my_data_files,
    options={"py2app": options},
    setup_requires=['py2app'],
    )
