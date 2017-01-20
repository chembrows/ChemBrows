#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets
from log import MyLog

from line_icon import ButtonLineIcon
import functions


class AdvancedSearch(QtWidgets.QDialog):

    """Class to perform advanced searches"""

    def __init__(self, parent=None):

        super(AdvancedSearch, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.parent = parent

        self.resource_dir, DATA_PATH = functions.getRightDirs()

        # Condition to use a specific logger if
        # module started in standalone
        if parent is None:
            self.logger = MyLog("activity.log")
            self.test = True
        else:
            self.logger = self.parent.l
            self.test = False

        self.options = QtCore.QSettings(DATA_PATH + "/config/searches.ini",
                                        QtCore.QSettings.IniFormat)

        # List to store the lineEdit, with the value of
        # the search fields
        self.fields_list = []

        self.initUI()
        self.defineSlots()
        self.restoreSettings()


    def restoreSettings(self):

        """Restore the right number of tabs"""

        for query in self.options.childGroups():
            # Don't create a search tab for the to read list
            if query == "ToRead":
                continue
            self.tabs.addTab(self.createForm(), query)

        # Try to restore the geometry of the AdvancedSearch window
        try:
            self.restoreGeometry(self.options.value("window_geometry"))
        except TypeError:
            self.logger.debug("Can't restore window geometry for AdvancedSearch")


    def closeEvent(self, event):

        """Actions to perform when closing the window.
        Mainly saves the window geometry"""

        self.logger.debug("Saving windows state for AdvancedSearch")
        self.options.setValue("window_geometry", self.saveGeometry())

        super(AdvancedSearch, self).closeEvent(event)


    def defineSlots(self):

        """Establish the slots"""

        self.button_search_and_save.clicked.connect(self.saveSearch)

        self.tabs.currentChanged.connect(self.tabChanged)

        self.button_delete_search.clicked.connect(self.deleteSearch)

        self.destroyed.connect(self.closeEvent)


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
        lines = self.tabs.currentWidget().findChildren(QtWidgets.QLineEdit)
        radios = self.tabs.currentWidget().findChildren(QtWidgets.QRadioButton)

        # Clean the fields of tailing comma
        topic_entries = [line.text()[:-1] if line.text() and line.text()[-1] == ',' else line.text() for line in lines[0:2]]
        author_entries = [line.text()[:-1] if line.text() and line.text()[-1] == ',' else line.text() for line in lines[2:4]]
        radio_states = [radio.isChecked() for radio in radios]

        base = functions.buildSearch(topic_entries, author_entries,
                                     radio_states)

        return base


    def tabChanged(self):

        """Method called when tab is changed.
        Fill the fields with the good data"""

        # Get the current tab number
        index = self.tabs.currentIndex()
        tab_title = self.tabs.tabText(index)

        # Get the lineEdit objects of the current search tab displayed
        lines = self.tabs.currentWidget().findChildren(QtWidgets.QLineEdit)
        topic_entries = [line for line in lines[0:2]]
        author_entries = [line for line in lines[2:4]]

        radios = self.tabs.currentWidget().findChildren(QtWidgets.QRadioButton)

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

            radio_states = self.options.value("{0}/radio_states".format(tab_title), None)
            radio_states = [True if element == 'true' else False for element in radio_states]
            if radio_states is not None:
                [radio.setChecked(value) for radio, value in zip(radios, radio_states)]

        else:
            self.button_delete_search.hide()


    def saveSearch(self):

        """Slot to save a query"""

        lines = self.tabs.currentWidget().findChildren(QtWidgets.QLineEdit)
        radios = self.tabs.currentWidget().findChildren(QtWidgets.QRadioButton)

        # Get the name of the current tab. Used to determine if the current
        # tab is the "new query" tab
        tab_title = self.tabs.tabText(self.tabs.currentIndex())

        topic_entries = [line.text() for line in lines[0:2]]
        author_entries = [line.text() for line in lines[2:4]]
        radio_states = [radio.isChecked() for radio in radios]

        # Build the query string
        base = self.buildSearch()

        if not base:
            return

        # Creating a new search
        if tab_title == "New query":
            # Get the search name with a dialogBox, if the user pushed the
            # save button
            name_search = QtWidgets.QInputDialog.getText(self, "Search name",
                                                     "Save your search as:")

            if "/" in name_search:
                name_search = name_search.replace("/", "-")

            if not name_search[1] or name_search[0] == "":
                return
            else:
                name_search = name_search[0]
            if name_search in self.options.childGroups():
                # Display an error message if the search name is already used
                QtWidgets.QMessageBox.critical(self, "Saving search", "You already have a search called like this",
                                           QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)

                self.logger.debug("This search name is already used")
                return
            else:
                self.tabs.addTab(self.createForm(), name_search)
                if not self.test:
                    self.parent.createSearchTab(name_search, base,
                                                topic_entries,
                                                author_entries,
                                                radio_states)
                    self.parent.loadNotifications()

                # Clear the fields when perform search
                for line in lines:
                    line.clear()

        # Modifying and saving an existing search
        else:
            name_search = tab_title

            if not self.test:
                self.parent.createSearchTab(name_search, base, topic_entries,
                                            author_entries, radio_states,
                                            update=True)

        self.logger.debug("Saving the search")

        self.options.beginGroup(name_search)

        # Re-initialize the keys
        self.options.remove("")
        if topic_entries != [''] * 2:
            self.options.setValue("topic_entries", topic_entries)
        if author_entries != [''] * 2:
            self.options.setValue("author_entries", author_entries)
        if base:
            self.options.setValue("sql_query", base)
        self.options.setValue("radio_states", radio_states)
        self.options.endGroup()

        self.options.sync()


    def showInfo(self, field_type):

        if field_type == 1:
            # Generic message fot the field tooltips
            mes = """
            Insert comma(s) between keywords. Ex: heparin sulfate, \
            heparinase. If 'Any' is checked, will match any keyword. If 'All' \
            is checked, will match all the keywords.\nWildcards (*) are \
            accepted. Ex: heparin*.\nFilters are case insensitive.
            """
        if field_type == 2:
            # Generic message fot the field tooltips
            mes = """
            Insert comma(s) between keywords. Ex: heparin sulfate, \
            heparinase.\nWildcards (*) are accepted. Ex: heparin*.\nFilters \
            are case insensitive.
            """
        elif field_type == 3:
            # Generic message fot the authors tooltips
            mes = """Insert comma(s) between keywords. Ex: Jean-Patrick \
            Francoia, Laurent Vial. If 'Any' is checked, will match any \
            author. If 'All' is checked, will match all the authors. \
            Wildcards (*) are accepted. Ex: J* Francoia. \nFilters are case \
            insensitive.\nFirst name comes before last name. Ex: Linus \
            Pauling or L* Pauling.
            """
        elif field_type == 4:
            # Generic message fot the authors tooltips
            mes = """Insert comma(s) between keywords. Ex: Jean-Patrick \
            Francoia, Laurent Vial. Wildcards (*) are accepted. \
            Ex: J* Francoia. \nFilters are case insensitive.\nFirst name \
            comes before last name. Ex: Linus Pauling or L* Pauling.
            """

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")

        QtWidgets.QMessageBox.information(self, "Information", mes,
                                      QtWidgets.QMessageBox.Ok)


    def createForm(self):

        # ------------------------ NEW SEARCH TAB -----------------------------

        # Main widget of the tab, with a grid layout
        widget_query = QtWidgets.QWidget()

        vbox_query = QtWidgets.QVBoxLayout()
        widget_query.setLayout(vbox_query)

        vbox_query.addStretch(1)

        # ------------- TOPIC ----------------------------------
        # Create a groupbox for the topic
        group_topic = QtWidgets.QGroupBox("Topic")
        grid_topic = QtWidgets.QGridLayout()
        group_topic.setLayout(grid_topic)

        # Add the topic groupbox to the global vbox
        vbox_query.addWidget(group_topic)

        # Create 3 lines, with their label: AND, OR, NOT
        label_topic_include = QtWidgets.QLabel("Include:")
        line_topic_include = ButtonLineIcon(os.path.join(self.resource_dir,
                                                     'images/info'))
        line_topic_include.buttonClicked.connect(lambda: self.showInfo(1))

        group_radio_topic = QtWidgets.QButtonGroup()
        radio_topic_any = QtWidgets.QRadioButton("Any")
        radio_topic_any.setChecked(True)
        radio_topic_all = QtWidgets.QRadioButton("All")
        group_radio_topic.addButton(radio_topic_any)
        group_radio_topic.addButton(radio_topic_all)

        label_topic_exclude = QtWidgets.QLabel("Exclude:")
        line_topic_exclude = QtWidgets.QLineEdit()
        line_topic_exclude = ButtonLineIcon(os.path.join(self.resource_dir,
                                                     'images/info'))
        line_topic_exclude.buttonClicked.connect(lambda: self.showInfo(2))

        # Organize the lines and the lab within the grid
        # addWidget (self, QWidget, int row, int column, int rowSpan, int columnSpan, Qt.Alignment alignment = 0)
        grid_topic.addWidget(label_topic_include, 0, 0)
        grid_topic.addWidget(line_topic_include, 0, 1)
        grid_topic.addWidget(radio_topic_any, 0, 2)
        grid_topic.addWidget(radio_topic_all, 0, 3)
        grid_topic.addWidget(label_topic_exclude, 1, 0)
        grid_topic.addWidget(line_topic_exclude, 1, 1)

        vbox_query.addStretch(1)

        # ------------- AUTHORS ----------------------------------
        # Create a groupbox for the authors
        group_author = QtWidgets.QGroupBox("Author(s)")
        grid_author = QtWidgets.QGridLayout()
        group_author.setLayout(grid_author)

        # Add the author groupbox to the global vbox
        vbox_query.addWidget(group_author)

        label_author_include = QtWidgets.QLabel("Include:")
        line_author_include = QtWidgets.QLineEdit()
        line_author_include = ButtonLineIcon(os.path.join(self.resource_dir,
                                                      'images/info'))
        line_author_include.buttonClicked.connect(lambda: self.showInfo(3))

        group_radio_author = QtWidgets.QButtonGroup()
        radio_author_any = QtWidgets.QRadioButton("Any")
        radio_author_any.setChecked(True)
        radio_author_all = QtWidgets.QRadioButton("All")
        group_radio_author.addButton(radio_author_any)
        group_radio_author.addButton(radio_author_all)

        label_author_not = QtWidgets.QLabel("Exclude:")
        line_author_exclude = QtWidgets.QLineEdit()
        line_author_exclude = ButtonLineIcon(os.path.join(self.resource_dir,
                                                      'images/info'))
        line_author_exclude.buttonClicked.connect(lambda: self.showInfo(4))

        grid_author.addWidget(label_author_include, 0, 0)
        grid_author.addWidget(line_author_include, 0, 1)
        grid_author.addWidget(radio_author_any, 0, 2)
        grid_author.addWidget(radio_author_all, 0, 3)
        grid_author.addWidget(label_author_not, 1, 0)
        grid_author.addWidget(line_author_exclude, 1, 1)

        vbox_query.addStretch(1)

        line_topic_include.returnPressed.connect(self.saveSearch)
        line_topic_exclude.returnPressed.connect(self.saveSearch)
        line_author_include.returnPressed.connect(self.saveSearch)
        line_author_exclude.returnPressed.connect(self.saveSearch)

        return widget_query


    def initUI(self):

        """Handles the display"""

        self.setWindowTitle('Advanced Search')

        self.tabs = QtWidgets.QTabWidget()

        query = self.createForm()

        self.tabs.addTab(query, "New query")

        # ----------------- BUTTONS -----------------------------------------

        self.button_delete_search = QtWidgets.QPushButton("Delete search", self)
        self.button_search_and_save = QtWidgets.QPushButton("Save search", self)

        # ------------------------ ASSEMBLING ---------------------------------

        # Create a global vbox, and stack the main widget + the search button
        self.vbox_global = QtWidgets.QVBoxLayout()
        self.vbox_global.addWidget(self.tabs)

        self.vbox_global.addWidget(self.button_delete_search)
        self.button_delete_search.hide()
        self.vbox_global.addWidget(self.button_search_and_save)

        self.setLayout(self.vbox_global)
        self.show()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    obj = AdvancedSearch()
    sys.exit(app.exec_())
