#!/usr/bin/python
# coding: utf-8


import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import feedparser
import validators

from log import MyLog
import hosts
import functions


class WizardAddJournal(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(WizardAddJournal, self).__init__(parent)

        self.TIMEOUT = 60

        self.setModal(True)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.parent = parent

        self.resource_dir, self.DATA_PATH = functions.getRightDirs()

        if parent is None:
            self.l = MyLog("activity.log")

            # Dummy file for saving if testing
            self.options = QtCore.QSettings("debug/options.ini",
                                            QtCore.QSettings.IniFormat)

            self.test = True
        else:
            self.l = self.parent.l
            self.options = self.parent.options
            self.test = False

        self.initUI()
        self.defineSlots()


    def defineSlots(self):

        """Establish the slots"""

        # When clicking OK, verify the user's input
        self.ok_button.clicked.connect(self.verifyInput)

        # Display help
        self.help_button.clicked.connect(self.showHelp)


    def _checkIsFeed(self, url: str, company: str,
                     feed: feedparser.util.FeedParserDict) -> bool:

        self.l.debug("Entering _checkIsFeed")

        # Check if the feed has a title
        try:
            journal = feed['feed']['title']
        except Exception as e:
            self.l.critical("verifyInput, can't access title {}".
                            format(url), exc_info=True)
            return False

        nbr_ok = 0
        for entry in feed.entries:

            try:
                doi = hosts.getDoi(company, journal, entry)
                url = hosts.refineUrl(company, journal, entry)
                self.l.debug("{}, {}".format(doi, url))
            except Exception as e:
                self.l.error("verifyInput, entry has no doi or no url".
                             format(url), exc_info=True)
                continue

            # Check if DOI and URL can be obtained
            if (doi.startswith('10.') and validators.url(url) or
                    validators.url(doi) and validators.url(url)):
                nbr_ok += 1

            # If 3 entries are OK, the feed is considered valid
            if nbr_ok == 3:
                self.l.debug("3 entries ok, valid feed")
                return True

        # If still here, the feed is NOT considered valid
        return False


    def _getFeed(self, url: str, timeout: int) -> feedparser.util.FeedParserDict:

        self.l.debug("Entering _getFeed")

        # Try to dl the RSS feed page
        try:
            # Get the RSS page of the url provided
            feed = feedparser.parse(url, timeout=timeout)

            self.l.debug("Add journal, RSS page successfully dled")

            return feed

        except Exception as e:
            self.l.error("Add journal feed {} could not be downloaded: {}".
                         format(url, e), exc_info=True)
            return None


    def verifyInput(self):

        """Verify the input. Dl the RSS page and check it belongs to a journal.
        Then, call the method to save the journal"""

        abb = self.line_abbreviation.text().strip()
        url = self.line_url_journal.text().strip()
        company = self.combo_publishers.currentText()

        self.l.debug("Starting verifyInput: {}, {}, {}".
                     format(abb, url, company))

        feed = self._getFeed(url, timeout=self.TIMEOUT)

        if feed is None:
            self.l.critical("verifyInput, feed is None")

            # Create error message if RSS page can't be downloaded
            error_mes = "An error occured while downloading the RSS page.\
                         Are you sure you have the right URL ?\
                         Try again later, maybe ?"
            error_mes = error_mes.replace("    ", "")
            QtWidgets.QMessageBox.critical(self,
                                           "Error while adding new journal",
                                           error_mes, QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

        is_feed = self._checkIsFeed(url, company, feed)

        if not is_feed:
            self.l.critical("verifyInput, not a valid feed")

            # Create error message if RSS page can't be downloaded
            error_mes = "The URL you provided does not match a valid RSS feed.\
                         Are you sure you have the right URL ?"
            error_mes = error_mes.replace("    ", "")
            QtWidgets.QMessageBox.critical(self,
                                           "Error while adding new journal",
                                           error_mes, QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return

        title = feed['feed']['title']
        mes = "The following journal will be added to your selection:\n{}"
        mes = mes.format(title)

        self.l.debug("New journal {} about to be added".format(title))

        # Confirmation dialog box
        choice = QtWidgets.QMessageBox.information(self, "Verification",
                                                   mes,
                                                   QtWidgets.QMessageBox.Cancel |
                                                   QtWidgets.QMessageBox.Ok,
                                                   defaultButton=QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Cancel:
            return
        else:
            self.l.debug("Try to save the new journal")
            self.saveJournal(title, abb, url, company)


    def showHelp(self):

        """Help displayed in a dialog box to help the user when adding
        a new journal"""

        mes = """Define the abbreviation of the journal you want to add.\n\n\
        Find the URL of the RSS page of the journal you want to add.\n\n\
        Publisher: to which publisher does the new journal belong ? This\
         choice will help ChemBrows to format the articles.\n\
        NOTE: Nature2 is for journals with a RSS feed formatted like Sci. Rep.
        """

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")

        QtWidgets.QMessageBox.information(self, "Information", mes,
                                          QtWidgets.QMessageBox.Ok)


    def initUI(self):

        """Handles the display"""

        self.setWindowTitle('Adding new journal')

        # Open a dialog box to explain how to add a journal
        self.help_button = QtWidgets.QPushButton("Help")

        # Validate. Triggers verification process
        self.ok_button = QtWidgets.QPushButton("Add journal")

        self.form_layout = QtWidgets.QFormLayout()

        self.line_abbreviation = QtWidgets.QLineEdit()
        self.line_abbreviation.setPlaceholderText("Ex: Chem. Commun.")

        self.line_url_journal = QtWidgets.QLineEdit()
        self.line_url_journal.setPlaceholderText("http://feeds.rsc.org/rss/cc")

        list_publishers = sorted(hosts.getAllCompanies())
        self.combo_publishers = QtWidgets.QComboBox()
        self.combo_publishers.addItems(list_publishers)

        self.form_layout.addRow(self.help_button)
        self.form_layout.addRow("Journal abbreviation:",
                                self.line_abbreviation)
        self.form_layout.addRow("URL RSS page:", self.line_url_journal)
        self.form_layout.addRow("Publisher:", self.combo_publishers)


# ------------------------ ASSEMBLING -----------------------------------------

        self.vbox_global = QtWidgets.QVBoxLayout()

        self.vbox_global.addLayout(self.form_layout)
        self.vbox_global.addWidget(self.ok_button)

        self.setLayout(self.vbox_global)
        self.show()

    def saveJournal(self, title, abb, url, company):

        """Will save the new journal, in file company.ini located in
        the user directory"""

        mes = "Journal already in the catalog"

        # Check if the RSS page's URL is not present in any company file
        for company in hosts.getAllCompanies():
            data_company = hosts.getJournals(company)

            # If URL already present, display error dialog box
            if url in data_company[2]:
                QtWidgets.QMessageBox.critical(self, "Error", mes,
                                               QtWidgets.QMessageBox.Ok)
                self.l.debug("URL {} already in catalog".format(url))
                return

        try:
            # If still here, write the new journal
            with open(os.path.join(self.DATA_PATH, "journals/{}.ini".
                      format(company)), 'a', encoding='utf-8') as out:
                out.write("{} : {} : {}".format(title, abb, url))
            self.l.debug("New journal written user side")
            self.l.debug("{} : {} : {}".format(title, abb, url))
            self.l.info("{} added to the catalog".format(title))
        except Exception as e:
            self.l.error("saveJournal, error writing journal: {}".format(e),
                         exc_info=True)
            return

        # Refresh parent check boxes and close
        if self.parent is not None:
            self.parent.displayJournals()
            self.parent.saveSettings()

        self.close()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    # parent = QtWidgets.QWidget()
    obj = WizardAddJournal()
    sys.exit(app.exec_())
