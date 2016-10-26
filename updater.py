#!/usr/bin/python
# coding: utf-8


from PyQt4 import QtCore

# TEST
from pyupdater.client import Client
from client_config import ClientConfig

# Perso
from log import MyLog
import functions

# DEBUG
import datetime


class Updater(QtCore.QThread):

    """Class to update ChemBrows, thanks to PyUpdater.
    Checks if an update is available on the remote server, downloads it, and
    overwrite the current app. Inherits from QThread to perform the update
    while displaying a QProgressBar"""

    def __init__(self, logger):

        QtCore.QThread.__init__(self)

        self.l = logger

        # Get the current version
        version = functions.getVersion()

        self.l.info("You are running ChemBrows version: {}".format(version))

        # Initialize client & call refresh to get latest update data
        client = Client(ClientConfig())
        client.refresh()

        # add progress hooks
        client.add_progress_hook(self._printStatus)

        # Returns an AppUpdate object if there is an update available
        self.app = client.update_check(client.app_name, version)

        if self.app is not None:
            self.update_available = True
        else:
            self.update_available = False


    def _printStatus(info):

        # TODO: does this function print anything at all ?

        total = info.get(u'total')

        downloaded = info.get(u'downloaded')

        status = info.get(u'status')

        print(downloaded, total, status)


    def run(self):

        """Main function of the class. Will be started from gui.py.
        Download the new version if availble, check if the download
        went ok, extract it, and overwrite the current app. Then the GUI
        will ask the user to restart."""

        # Check if a new version is available
        if self.app is not None:
            self.l.info("A new version of ChemBrows is available")
            try:
                self.l.debug("Starting dl of new version")
                # First, download the new version
                self.app.download()

                # Ensure file dled successfully
                if self.app.is_downloaded():
                    self.l.info("New version dled. Starting extract/overwrite")

                    # Extract and overwrite current application
                    self.app.extract_overwrite()
                    self.l.info("New version installed. You should restart")

            except Exception as e:
                self.l.critical("ERROR UPDATING APP: {}".format(e),
                                exc_info=True)


if __name__ == '__main__':
    logger = MyLog()
    updater = Updater(logger)
