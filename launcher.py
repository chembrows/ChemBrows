#!/usr/bin/python
# coding: utf-8

import os
import sys
from PyQt4 import QtGui
import shutil

from gui import MyWindow
import constants
from log import MyLog



if __name__ == '__main__':

    # Check if the running ChemBrows is a frozen app
    if getattr(sys, "frozen", False):

        # The program is NOT in debug mod if it's frozen
        debug_mod = False
        DATA_PATH = constants.DATA_PATH

        # http://stackoverflow.com/questions/10293808/how-to-get-the-path-of-the-executing-frozen-script
        resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        QtGui.QApplication.addLibraryPath(resource_dir)

        # Create the user directory if it doesn't exist
        os.makedirs(DATA_PATH, exist_ok=True)

        with open(os.path.join(resource_dir, 'config/version.txt'),
                  'r') as version_file:

            version = version_file.read()

        # Create the logger w/ the appropriate size
        l = MyLog(DATA_PATH + "/activity.log")
        l.info("Houston, this is updater speaking")

        new_directory = os.path.join(resource_dir, 'new_version')

        if os.path.exists(new_directory):
            for f in os.listdir(new_directory):

                new_f = os.path.join(new_directory, f)

                if os.path.isfile(new_f):
                    shutil.copy(new_f, resource_dir)
                    print("file" + new_f)
                else:
                    print("dir:" + new_f)
                    try:
                        shutil.rmtree(os.path.join(resource_dir, f))
                    except FileNotFoundError:
                        pass
                    shutil.copytree(new_f, os.path.join(resource_dir, f))


    app = QtGui.QApplication(sys.argv)
    ex = MyWindow()
    app.processEvents()
    sys.exit(app.exec_())
