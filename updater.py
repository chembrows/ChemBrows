#!/usr/bin/python
# coding: utf-8


import sys
import esky
from PyQt4 import QtCore
import traceback


# DEBUG
import datetime

from log import MyLog


class Updater(QtCore.QThread):

    """Class to update ChemBrows, through an Esky object.
    Looks on the server if an update is available, and dl it.
    Inherits from QThread to perform the update while displaying
    a QProgressBar"""

    def __init__(self, logger):

        QtCore.QThread.__init__(self)

        self.l = logger
        self.update_available = False

        self.app = esky.Esky(sys.executable, "http://chembrows.com/downloads/updates/")

        # Get the number of the latest version
        try:
            best_version = self.app.find_update()
        except Exception as e:
            self.l.critical("ERROR FINDING VERSION APP: {}".format(e))
            return None

        if best_version is None:
            self.l.info("Latest version of ChemBrows running: {}".format(self.app.version))
        else:
            self.l.info("Latest version available: {}. Running version : {}".format(best_version, self.app.active_version))
            self.update_available = True


    def __del__(self):

        """Method to destroy the thread properly"""

        self.l.debug("Deleting thread")
        self.exit()


    def run(self):

        try:
            # Update ChemBrows
            self.app.get_root()
            self.app.auto_update()
            # self.app.cleanup()
            # self.app.drop_root()
        except Exception as e:
            self.l.critical("ERROR UPDATING APP: {}".format(e))
            self.l.error(traceback.format_exc())
