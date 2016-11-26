#!/usr/bin/python
# coding: utf-8


import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import feedparser

from log import MyLog
import hosts
import functions


class WizardJournal(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(WizardJournal, self).__init__(parent)
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

        self.check_journals = []

        self.initUI()
        self.defineSlots()


    def defineSlots(self):

        """Establish the slots"""

        # When clicking OK, verify the user's input
        self.ok_button.clicked.connect(self.verifyInput)

        # Display help
        self.help_button.clicked.connect(self.showHelp)


    def verifyInput(self):

        """Verify the input. Dl the RSS page and check it belongs to a journal.
        Then, call the method to save the journal"""

        abb = self.line_abbreviation.text()
        url = self.line_url_journal.text()
        publisher = self.combo_publishers.currentText()

        # Create error message if RSS page can't be downloaded
        error_mes = "An error occured while downloading the RSS page.\
                     Are you sure you have the right URL ?\
                     Try again later, maybe ?"
        error_mes = error_mes.replace("    ", "")

        try:
            feed = feedparser.parse(url, timeout=60)
            self.l.info("verifyInput: RSS page successfully dled")
        except Exception as e:
            self.l.error("verifyInput: RSS page could not be downloaded",
                         exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error while adding new journal",
                                       error_mes, QtWidgets.QMessageBox.Ok,
                                       defaultButton=QtWidgets.QMessageBox.Ok)
            return

        mes = "The following journal will be added to your selection:\n{}"

        try:
            title = feed['feed']['title']
            mes = mes.format(title)

            # Confirmation dialog box
            choice = QtWidgets.QMessageBox.information(self, "Verification", mes,
                                                   QtWidgets.QMessageBox.Cancel |
                                                   QtWidgets.QMessageBox.Ok,
                                                   defaultButton=QtWidgets.QMessageBox.Cancel)

            if choice == QtWidgets.QMessageBox.Cancel:
                return
            else:
                self.l.debug("Try to save the new journal")
                self.saveJournal(title, abb, url, publisher)

        except KeyError:
            self.l.critical("No title for the journal ! Aborting")
            self.l.critical(url)
            QtWidgets.QMessageBox.critical(self, "Error while adding new journal",
                                       error_mes, QtWidgets.QMessageBox.Ok,
                                       defaultButton=QtWidgets.QMessageBox.Ok)
            return


    def showHelp(self):

        """Help displayed in a dialog box to help the user when adding
        a new journal"""

        mes = """Define the abbreviation of the journal you want to add.\n\n\
        Find the URL of the RSS page of the journal you want to add.\n\n\
        Publisher: to which publisher does the new journal belong ? This\
         choice will help ChemBrows to format the articles.
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
        self.ok_button = QtWidgets.QPushButton("OK")

        self.form_layout = QtWidgets.QFormLayout()

        self.line_abbreviation = QtWidgets.QLineEdit()
        self.line_abbreviation.setPlaceholderText("Ex: Chem. Commun.")

        self.line_url_journal = QtWidgets.QLineEdit()
        self.line_url_journal.setPlaceholderText("http://feeds.rsc.org/rss/cc")

        list_publishers = sorted(hosts.getCompanies())
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


    def saveJournal(self, title, abb, url, publisher):

        """Will save the new journal, in file publisher.ini located in
        the user directory"""

        mes = "Journal already in the catalog"

        # Check if the RSS page's URL is not present in any publisher file
        for company in hosts.getCompanies():
            data_company = hosts.getJournals(company)

            # If URL already present, display error dialog box
            if url in data_company[2]:
                QtWidgets.QMessageBox.critical(self, "Error", mes,
                                           QtWidgets.QMessageBox.Ok)
                return

        # If still here, write the new journal
        with open(os.path.join(self.DATA_PATH, "journals/{}.ini".
                  format(publisher)), 'a') as out:
            out.write("{} : {} : {}".format(title, abb, url))

        self.close()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    # parent = QtWidgets.QWidget()
    obj = WizardJournal()
    sys.exit(app.exec_())
