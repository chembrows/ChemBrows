#!/usr/bin/python
# coding: utf-8


from PyQt5 import QtCore

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

    def __init__(self, logger, callback=None):

        QtCore.QThread.__init__(self)

        self.callback = callback

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
            self.l.info("Version {} is available".format(self.app.latest))
        else:
            self.update_available = False


    def _printStatus(self, info):

        """Print the numbers of bytes dled for the new version.
        Also calls a callback to display a percentage progress bar during
        dl"""

        total = info.get(u'total')

        downloaded = info.get(u'downloaded')

        status = info.get(u'status')

        percent = downloaded * 100 / total

        self.l.info("{}/{}, {}".format(downloaded, total, status))

        if self.callback is not None:
            # send the percentage dled to callback
            self.callback(percent)


    def run(self):

        """Main function of the class. Will be started from gui.py.
        Download the new version if availble, check if the download
        went ok, extract it, and overwrite the current app. Then the GUI
        will ask the user to restart."""

        # Check if a new version is available
        if self.app is not None:
            self.l.info("A new version of ChemBrows is available")

            self.l.debug("Starting dl of new version")
            try:
                # First, download the new version
                self.app.download()
                self.l.info("New version dled")
            except Exception as e:
                self.l.critical("ERROR DOWNLOADING NEW VERSION: {}".format(e),
                                exc_info=True)


if __name__ == '__main__':
    logger = MyLog()
    updater = Updater(logger)
