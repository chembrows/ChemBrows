#!/usr/bin/python
# -*-coding:Utf-8 -*

# http://stackoverflow.com/questions/14215303/scipy-with-py2exe
# http://stackoverflow.com/questions/11308941/executable-created-by-py2exe-not-working
# http://www.py2exe.org/index.cgi/data_files
# http://stackoverflow.com/questions/2747860/having-py2exe-include-my-data-files-like-include-package-data
# http://stackoverflow.com/questions/1570542/when-using-py2exe-pyqt-application-cannot-load-sqlite-database

from distutils.core import setup
import py2exe
import os


my_data_files = []

# Copy the images for the GUI
for file in os.listdir('./images/'):
    f1 = './images/' + file
    if os.path.isfile(f1):  # skip directories
        f2 = 'images', [f1]
        my_data_files.append(f2)

# Copy the config files for the journals
for file in os.listdir('./journals/'):
    f1 = './journals/' + file
    if os.path.isfile(f1):  # skip directories
        f2 = 'journals', [f1]
        my_data_files.append(f2)

# Copy the config files
for file in os.listdir('./config/'):
    f1 = './config/' + file
    if os.path.isfile(f1):  # skip directories
        f2 = 'config', [f1]
        my_data_files.append(f2)

# Create an empty directory to store the graphical abstracts
my_data_files.append(('graphical_abstracts/', ''))

# Copy the sqlite driver
my_data_files.append(('sqldrivers', ('C:\Python34\Lib\site-packages\PyQt4\plugins\sqldrivers\qsqlite4.dll',)))

# Copy the plugins to load images
for file in os.listdir('C:\Python34\Lib\site-packages\PyQt4\plugins\imageformats\\'):
    f1 = 'C:\Python34\Lib\site-packages\PyQt4\plugins\imageformats\\' + file
    if os.path.isfile(f1):  # skip directories
        f2 = 'imageformats', [f1]
        my_data_files.append(f2)

setup(
    windows=[{'script': 'gui.py'}],
    data_files=my_data_files,
    options={
        'py2exe': {
            'compressed': True,
            'optimize': 2,
            # 'excludes': [
                # '_gtkagg',
                # '_tkagg',
                # '_agg2',
                # '_cairo',
                # '_cocoaagg',
                # '_fltkagg',
                # '_gtk',
                # '_gtkcairo',
                # '_ssl',
                # 'doctest',
                # 'pdb',
                # 'unitest',
                # 'pydoc_data',
                # 'tcl'
                # ]
            'includes': [
                'sip',
                'PyQt4.QtCore',
                'PyQt4.QtGui',
                'PyQt4.QtNetwork',
                'PyQt4.QtSql',
                'scipy.sparse.csgraph._validation',
                'sklearn.utils.sparsetools._graph_validation',
                'scipy.special._ufuncs_cxx'
                ]
            }
        },
    )
