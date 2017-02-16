#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets

from log import MyLog
from wizard_add_journal import WizardAddJournal
from wizard_del_journal import WizardDelJournal
import hosts
import functions


class Settings(QtWidgets.QDialog):

    """Class for the program settings, modifiable by the user.
    Creates a child window"""

    def __init__(self, parent=None):

        super(Settings, self).__init__(parent)

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
        self.connexion()
        self.defineSlots()


    def connexion(self):

        """Get the settings and restore them"""

        journals_to_parse = self.options.value("journals_to_parse", [])

        # Check the boxes
        if not journals_to_parse:
            return
        else:
            for box in self.check_journals:
                if box.text() in journals_to_parse:
                    box.setCheckState(2)
                else:
                    box.setCheckState(0)


    def defineSlots(self):

        """Establish the slots"""

        # To close the window and save the settings
        self.ok_button.clicked.connect(self.saveSettings)


        # Button "clean database" (erase the unintersting journals from the db)
        # connected to the method of the main window class
        # TO COMMENT to run the module standalone
        if not self.test:
            self.button_clean_db.clicked.connect(self.parent.cleanDb)
            self.button_reset_db.clicked.connect(self.parent.resetDb)
            self.button_erase_db.clicked.connect(self.parent.eraseDb)


    def dialogManageJournals(self):

        """Opens a dialog, let the user choose between deleting and adding
        journals"""

        dial = QtWidgets.QDialog(self)

        label_choice = QtWidgets.QLabel("Would you like to:")

        button_add = QtWidgets.QPushButton("Add a journal")
        button_del = QtWidgets.QPushButton("Delete a journal")

        button_add.clicked.connect(dial.accept)
        button_add.clicked.connect(lambda: WizardAddJournal(self))

        button_del.clicked.connect(dial.accept)
        button_del.clicked.connect(lambda: WizardDelJournal(self))

        hbox_dial = QtWidgets.QHBoxLayout()
        hbox_dial.addWidget(button_add)
        hbox_dial.addWidget(button_del)

        vbox_dial = QtWidgets.QVBoxLayout()
        vbox_dial.addWidget(label_choice, alignment=QtCore.Qt.AlignHCenter)
        vbox_dial.addLayout(hbox_dial)

        dial.setLayout(vbox_dial)

        dial.show()


    def selectUnselectAll(self, state):

        """Select or unselect all the journals"""

        for box in self.check_journals:
            box.setCheckState(state)


    def clearLayout(self, layout):

        """Method to erase the widgets from a layout"""

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                    QtWidgets.qApp.processEvents()
                else:
                    self.clearLayout(item.layout())


    def displayJournals(self):

        """Display the checkboxes of the journals"""

        self.clearLayout(self.vbox_check_journals)

        self.check_journals = []

        self.button_manage_journals = QtWidgets.QPushButton("Manage journals")
        self.vbox_check_journals.addWidget(self.button_manage_journals)
        self.button_manage_journals.clicked.connect(self.dialogManageJournals)

        labels_checkboxes = []

        # Get labels of the future check boxes of the journals to be parsed
        for company in hosts.getCompanies():
            labels_checkboxes += hosts.getJournals(company)[1]

        labels_checkboxes.sort()

        self.box_select_all = QtWidgets.QCheckBox("Select all")
        self.box_select_all.setCheckState(0)
        self.vbox_check_journals.addWidget(self.box_select_all)

        # Checkbox to select/unselect all the journals
        self.box_select_all.stateChanged.connect(self.selectUnselectAll)

        # Build the checkboxes, and put them in a layout
        for label in labels_checkboxes:
            check_box = QtWidgets.QCheckBox(label)
            check_box.setCheckState(2)
            self.check_journals.append(check_box)
            self.vbox_check_journals.addWidget(check_box)

        # Restore check boxes states
        journals_to_parse = self.options.value("journals_to_parse", [])
        if not journals_to_parse:
            return
        else:
            for box in self.check_journals:
                if box.text() in journals_to_parse:
                    box.setCheckState(2)
                else:
                    box.setCheckState(0)


    def initUI(self):

        """Handles the display"""

        self.setWindowTitle('Settings')

        self.ok_button = QtWidgets.QPushButton("OK", self)

        self.tabs = QtWidgets.QTabWidget()

# ------------------------ JOURNALS TAB ---------------------------------------

        # Scroll area for the journals to check
        self.scroll_check_journals = QtWidgets.QScrollArea()
        self.scrolling_check_journals = QtWidgets.QWidget()
        self.vbox_check_journals = QtWidgets.QVBoxLayout()
        self.scrolling_check_journals.setLayout(self.vbox_check_journals)

        # Add the check boxes for all the journals
        self.displayJournals()

        self.scroll_check_journals.setWidget(self.scrolling_check_journals)

        self.tabs.addTab(self.scroll_check_journals, "Journals")

# ------------------------ DATABASE TAB ---------------------------------------

        self.widget_database = QtWidgets.QWidget()
        self.vbox_database = QtWidgets.QVBoxLayout()

        mes = """
        Click on the buttons to display help.
        Confirmation will be asked before anything
        is done to your data: no worries.
        """
        mes = mes.replace("    ", "")
        self.label_explain = QtWidgets.QLabel(mes)

        self.button_clean_db = QtWidgets.QPushButton("Clean database")
        self.button_reset_db = QtWidgets.QPushButton("Reset database")
        self.button_erase_db = QtWidgets.QPushButton("Erase database")

        # Create an empty widget to act as a spacer
        empty_widget = QtWidgets.QWidget()
        empty_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                   QtWidgets.QSizePolicy.Expanding)

        # Add the spacer between each button
        self.vbox_database.addWidget(self.label_explain,
                                     alignment=QtCore.Qt.AlignTop)
        self.vbox_database.addWidget(empty_widget)
        self.vbox_database.addWidget(self.button_clean_db)
        self.vbox_database.addWidget(empty_widget)
        self.vbox_database.addWidget(self.button_reset_db)
        self.vbox_database.addWidget(empty_widget)
        self.vbox_database.addWidget(self.button_erase_db)
        self.vbox_database.addWidget(empty_widget)

        self.widget_database.setLayout(self.vbox_database)

        self.tabs.addTab(self.widget_database, "Database")

# ------------------------ ASSEMBLING ------------------------------------------------

        self.vbox_global = QtWidgets.QVBoxLayout()
        self.vbox_global.addWidget(self.tabs)

        self.vbox_global.addWidget(self.ok_button)

        self.setLayout(self.vbox_global)
        self.show()


    def saveSettings(self):

        """Slot to save the settings"""

        journals_to_parse = []

        for box in self.check_journals:
            if box.checkState() == 2:
                journals_to_parse.append(box.text())

        if journals_to_parse:
            self.options.remove("journals_to_parse")
            self.options.setValue("journals_to_parse", journals_to_parse)
        else:
            self.options.remove("journals_to_parse")

        if not self.test:
            self.parent.model.submitAll()
            self.parent.displayTags()
            self.parent.resetView()

        # Close the settings window and free the memory
        self.close()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    obj = Settings()
    sys.exit(app.exec_())
