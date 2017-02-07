#!/usr/bin/python
# coding: utf-8


import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import feedparser

from log import MyLog
import hosts
import functions


class WizardDelJournal(QtWidgets.QDialog):

    """Simple wizard to help the user to delete the journals he added"""

    def __init__(self, parent=None):

        super(WizardDelJournal, self).__init__(parent)

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

        # Store the checkboxes of the window
        self.check_journals = []

        self.initUI()
        self.defineSlots()


    def defineSlots(self):

        """Establish the slots"""

        # Checkbox to select/unselect all the journals
        self.box_select_all.stateChanged.connect(self.selectUnselectAll)

        # Confirm deleting journals
        self.button_del.clicked.connect(self.confirmDelete)


    def selectUnselectAll(self, state):

        """Select or unselect all the journals"""

        for box in self.check_journals:
            box.setCheckState(state)


    def initUI(self):

        """Handle the display"""

        self.setWindowTitle('Deleting journals')

        self.vbox_global = QtWidgets.QVBoxLayout()

        # Open a dialog box to explain how to add a journal
        mes = "Confirmation will be asked before\nanything permanent is done: no worries"

        self.label_help = QtWidgets.QLabel(mes)
        self.vbox_global.addWidget(self.label_help)

        # Scroll area for the journals to check
        self.scroll_check_journals = QtWidgets.QScrollArea()
        self.scrolling_check_journals = QtWidgets.QWidget()
        self.vbox_check_journals = QtWidgets.QVBoxLayout()
        self.scrolling_check_journals.setLayout(self.vbox_check_journals)

        labels_checkboxes = []

        # Get labels of the future check boxes of the journals to be parsed
        # Only journals on user's side
        for company in hosts.getCompanies(user=True):
            labels_checkboxes += hosts.getJournals(company, user=True)[1]

        labels_checkboxes.sort()

        self.box_select_all = QtWidgets.QCheckBox("Select all")
        self.box_select_all.setCheckState(0)
        self.vbox_check_journals.addWidget(self.box_select_all)

        # Build the checkboxes, and put them in a layout
        for label in labels_checkboxes:
            check_box = QtWidgets.QCheckBox(label)
            check_box.setCheckState(0)
            self.check_journals.append(check_box)
            self.vbox_check_journals.addWidget(check_box)

        self.scroll_check_journals.setWidget(self.scrolling_check_journals)

        self.vbox_global.addWidget(self.scroll_check_journals)

        # Validate. Triggers verification process
        self.button_del = QtWidgets.QPushButton("Delete journal(s)")
        self.vbox_global.addWidget(self.button_del)

        self.setLayout(self.vbox_global)
        self.show()


    def confirmDelete(self):

        """Delete the journals selected by the user"""

        # Build a list of abb for the journals to delete
        j_to_del = []
        for box in self.check_journals:
            if box.checkState() == 2:
                j_to_del.append(box.text())

        if not j_to_del:
            return

        mes = """The selected journals will be deleted from the catalog. The 
        corresponding data will not be removed from your database until you 
        clean it (Settings > Database > Clean database"""

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")
        mes = mes.replace("\n", "")

        # Confirmation dialog box
        choice = QtWidgets.QMessageBox.information(self, "Confirm",
                                                   mes,
                                                   QtWidgets.QMessageBox.Cancel |
                                                   QtWidgets.QMessageBox.Ok,
                                                   defaultButton=QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Cancel:
            return
        else:
            self.l.debug("User confirmed deleting journals {}".
                         format(j_to_del))

        # For each company, open the ini file and check that each journal
        # IS NOT a journal to delete, then rewrite the file
        for company in os.listdir(os.path.join(self.DATA_PATH, 'journals')):

            with open(os.path.join(self.DATA_PATH, 'journals', company),
                      'r', encoding='utf-8') as config:

                lines = config.readlines()

            lines = [l for l in lines if not any(j in l for j in j_to_del)]

            with open(os.path.join(self.DATA_PATH, 'journals', company),
                      'w', encoding='utf-8') as config:

                for line in lines:
                    config.write(line)

        # Refresh parent check boxes and close
        self.parent.displayJournals()
        self.close()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    obj = WizardDelJournal()
    sys.exit(app.exec_())
