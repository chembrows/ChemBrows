#!/usr/bin/python
# coding: utf-8


import sys
# import os
from PyQt4 import QtGui, QtCore
from log import MyLog

import functions


class AdvancedSearch(QtGui.QDialog):

    """Class to perform advanced searches"""

    def __init__(self, parent):

        super(AdvancedSearch, self).__init__(parent)

        self.parent = parent

        # Condition to use a specific logger if
        # module started in standalone
        if type(parent) is QtGui.QWidget:
            self.logger = MyLog()
            self.test = True
        else:
            self.logger = self.parent.l
            self.test = False

        self.options = QtCore.QSettings("searches.ini", QtCore.QSettings.IniFormat)

        # List to store the lineEdit, with the value of
        # the search fields
        self.fields_list = []

        self.initUI()
        self.defineSlots()
        self.restoreSettings()


    def restoreSettings(self):

        """Restore the right number of tabs"""

        for query in self.options.childGroups():
            self.tabs.addTab(self.createForm(), query)


    def defineSlots(self):

        """Establish the slots"""

        self.button_search_and_save.clicked.connect(self.search)

        self.tabs.currentChanged.connect(self.tabChanged)

        self.button_delete_search.clicked.connect(self.deleteSearch)


    def deleteSearch(self):

        """Slot to delete a query"""

        # Get the title of the search, get the group with
        # the same name in searches.ini, and clear the group
        tab_title = self.tabs.tabText(self.tabs.currentIndex())
        self.options.beginGroup(tab_title)
        # Re-initialize the keys
        self.options.remove("")
        self.options.endGroup()

        self.tabs.removeTab(self.tabs.currentIndex())

        if not self.test:
            for index in range(self.parent.onglets.count()):
                if self.parent.onglets.tabText(index) == tab_title:
                    self.parent.list_tables_in_tabs.remove(self.parent.onglets.widget(index))
                    self.parent.onglets.removeTab(index)
                    self.parent.onglets.setCurrentIndex(0)
                    break


    def buildSearch(self):

        """Build the query"""

        # Get all the lineEdit from the current tab
        lines = self.tabs.currentWidget().findChildren(QtGui.QLineEdit)

        # Clean the fields of tailing comma
        topic_entries = [line.text()[:-1] if line.text() and line.text()[-1] == ',' else line.text() for line in lines[0:3]]
        author_entries = [line.text()[:-1] if line.text() and line.text()[-1] == ',' else line.text() for line in lines[3:7]]

        base = functions.buildSearch(topic_entries, author_entries)

        return base


    def tabChanged(self):

        """Method called when tab is changed.
        Fill the fields with the good data"""

        # Get the current tab number
        index = self.tabs.currentIndex()
        tab_title = self.tabs.tabText(index)

        # Get the lineEdit objects of the current search tab displayed
        lines = self.tabs.currentWidget().findChildren(QtGui.QLineEdit)
        topic_entries = [line for line in lines[0:3]]
        author_entries = [line for line in lines[3:7]]

        if index != 0:

            # Change the buttons at the button if the tab is
            # a tab dedicated to search edition
            self.button_delete_search.show()

            topic_entries_options = self.options.value("{0}/topic_entries".format(tab_title), None)
            if topic_entries_options is not None:
                topic_entries = [line.setText(value) for line, value in zip(topic_entries, topic_entries_options)]
            author_entries_options = self.options.value("{0}/author_entries".format(tab_title), None)
            if author_entries_options is not None:
                author_entries = [line.setText(value) for line, value in zip(author_entries, author_entries_options)]

        else:
            self.button_delete_search.hide()


    def search(self):

        """Slot to save a query"""

        lines = self.tabs.currentWidget().findChildren(QtGui.QLineEdit)

        # Get the name of the current tab. Used to determine if the current
        # tab is the "new query" tab
        tab_title = self.tabs.tabText(self.tabs.currentIndex())

        topic_entries = [line.text() for line in lines[0:3]]
        author_entries = [line.text() for line in lines[3:7]]

        # Build the query string
        base = self.buildSearch()

        if not base:
            return

        # Creating a new search
        if tab_title == "New query":
            # Get the search name with a dialogBox, if the user pushed the save button
            name_search = QtGui.QInputDialog.getText(self, "Search name", "Save your search as:")

            if "/" in name_search:
                name_search = name_search.replace("/", "-")

            if not name_search[1] or name_search[0] == "":
                return
            else:
                name_search = name_search[0]
            if name_search in self.options.childGroups():
                # Display an error message if the search name is already used
                QtGui.QMessageBox.critical(self, "Saving search", "You already have a search called like this",
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)

                self.logger.debug("This search name is already used")
                return
            else:
                self.tabs.addTab(self.createForm(), name_search)
                if not self.test:
                    self.parent.createSearchTab(name_search, base,
                                                topic_entries,
                                                author_entries)
                    self.parent.loadNotifications()

                # Clear the fields when perform search
                for line in lines:
                    line.clear()

        # Modifying and saving an existing search
        else:
            name_search = tab_title

            if not self.test:
                self.parent.createSearchTab(name_search, base, topic_entries,
                                            author_entries, update=True)

        self.logger.debug("Saving the search")

        self.options.beginGroup(name_search)

        # Re-initialize the keys
        self.options.remove("")
        # self.options.setValue("name_search", name_search)
        if topic_entries != [''] * 3:
            self.options.setValue("topic_entries", topic_entries)
        if author_entries != [''] * 3:
            self.options.setValue("author_entries", author_entries)
        if base:
            self.options.setValue("sql_query", base)
        self.options.endGroup()

        self.options.sync()


    def createForm(self):

        # ------------------------ NEW SEARCH TAB -----------------------------

        # Main widget of the tab, with a grid layout
        widget_query = QtGui.QWidget()

        vbox_query = QtGui.QVBoxLayout()
        widget_query.setLayout(vbox_query)

        vbox_query.addStretch(1)

        # ------------- TOPIC ----------------------------------
        # Create a groupbox for the topic
        group_topic = QtGui.QGroupBox("Topic")
        grid_topic = QtGui.QGridLayout()
        group_topic.setLayout(grid_topic)

        # Add the topic groupbox to the global vbox
        vbox_query.addWidget(group_topic)

        # Create 3 lines, with their label: AND, OR, NOT
        label_topic_and = QtGui.QLabel("AND:")
        line_topic_and = QtGui.QLineEdit()

        label_topic_or = QtGui.QLabel("OR:")
        line_topic_or = QtGui.QLineEdit()

        label_topic_not = QtGui.QLabel("NOT:")
        line_topic_not = QtGui.QLineEdit()

        # Organize the lines and the lab within the grid
        grid_topic.addWidget(label_topic_and, 0, 0)
        grid_topic.addWidget(line_topic_and, 0, 1, 1, 3)
        grid_topic.addWidget(label_topic_or, 1, 0)
        grid_topic.addWidget(line_topic_or, 1, 1, 1, 3)
        grid_topic.addWidget(label_topic_not, 2, 0)
        grid_topic.addWidget(line_topic_not, 2, 1, 1, 3)

        vbox_query.addStretch(1)

        # ------------- AUTHORS ----------------------------------
        # Create a groupbox for the authors
        group_author = QtGui.QGroupBox("Author(s)")
        grid_author = QtGui.QGridLayout()
        group_author.setLayout(grid_author)

        # Add the author groupbox to the global vbox
        vbox_query.addWidget(group_author)

        label_author_and = QtGui.QLabel("AND:")
        line_author_and = QtGui.QLineEdit()

        label_author_or = QtGui.QLabel("OR:")
        line_author_or = QtGui.QLineEdit()

        label_author_not = QtGui.QLabel("NOT:")
        line_author_not = QtGui.QLineEdit()

        grid_author.addWidget(label_author_and, 0, 0)
        grid_author.addWidget(line_author_and, 0, 1, 1, 3)
        grid_author.addWidget(label_author_or, 1, 0)
        grid_author.addWidget(line_author_or, 1, 1, 1, 3)
        grid_author.addWidget(label_author_not, 2, 0)
        grid_author.addWidget(line_author_not, 2, 1, 1, 3)

        vbox_query.addStretch(1)

        line_topic_and.returnPressed.connect(self.search)
        line_topic_or.returnPressed.connect(self.search)
        line_topic_not.returnPressed.connect(self.search)
        line_author_and.returnPressed.connect(self.search)
        line_author_or.returnPressed.connect(self.search)
        line_author_not.returnPressed.connect(self.search)

        return widget_query


    def initUI(self):

        """Handles the display"""

        self.parent.window_search = QtGui.QWidget()
        self.parent.window_search.setWindowTitle('Advanced Search')

        self.tabs = QtGui.QTabWidget()

        query = self.createForm()

        self.tabs.addTab(query, "New query")


        # ----------------- BUTTONS -----------------------------------------

        self.button_delete_search = QtGui.QPushButton("Delete search", self)
        self.button_search_and_save = QtGui.QPushButton("Save search", self)

        # ------------------------ ASSEMBLING ---------------------------------

        # Create a global vbox, and stack the main widget + the search button
        self.vbox_global = QtGui.QVBoxLayout()
        self.vbox_global.addWidget(self.tabs)

        self.vbox_global.addWidget(self.button_delete_search)
        self.button_delete_search.hide()
        self.vbox_global.addWidget(self.button_search_and_save)

        self.parent.window_search.setLayout(self.vbox_global)
        self.parent.window_search.show()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    parent = QtGui.QWidget()
    obj = AdvancedSearch(parent)
    sys.exit(app.exec_())
