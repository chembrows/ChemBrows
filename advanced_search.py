#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
from PyQt4 import QtGui, QtCore


class AdvancedSearch(QtGui.QDialog):

    """Class to perform advanced searches"""

    def __init__(self, parent):

        super(AdvancedSearch, self).__init__(parent)

        self.parent = parent

        #List to store the lineEdit, with the value of
        #the search fields
        self.fields_list = []

        self.initUI()
        self.defineSlots()


    #def connexion(self):

        #"""Get the settings and restore them"""

        #journals_to_parse = self.parent.options.value("journals_to_parse", [])

        ##Check the boxes
        #if not journals_to_parse:
            #return
        #else:
            #for box in self.check_journals:
                #if box.text() in journals_to_parse:
                    #box.setCheckState(2)
                #else:
                    #box.setCheckState(0)


    def defineSlots(self):

        """Establish the slots"""

        #To close the window and save the settings
        #self.ok_button.clicked.connect(self.saveSettings)

        #Button "clean database" (erase the unintersting journals from the db)
        #connected to the method of the main window class
        self.button_add.clicked.connect(self.addField)


    def addField(self):

        """Slot to add a research field to the query window.
        Only deals with the UI"""

        if len(self.fields_list) < 6:
            line_new_field = QtGui.QLineEdit()

            combo_operator = QtGui.QComboBox()
            combo_operator.addItems(["AND", "OR", "NOT"])

            combo_field_name = QtGui.QComboBox()
            combo_field_name.addItems(["Topic", "Author(s)"])

            self.fields_list.append((combo_operator, line_new_field, combo_field_name))

            self.grid_query.addWidget(combo_operator, 2 + len(self.fields_list), 0)
            self.grid_query.addWidget(line_new_field, 2 + len(self.fields_list), 1, 1, 2)
            self.grid_query.addWidget(combo_field_name, 2 + len(self.fields_list), 3)
        else:
            return


    def initUI(self):

        """Handles the display"""

        self.parent.window_search = QtGui.QWidget()
        self.parent.window_search.setWindowTitle('Advanced Search')

        self.search_button = QtGui.QPushButton("Search !", self)

        self.tabs = QtGui.QTabWidget()

#------------------------ NEW SEARCH TAB ------------------------------------------------

        #Main widget of the tab, with a grid layout
        self.widget_query = QtGui.QWidget()
        self.grid_query = QtGui.QGridLayout()
        self.widget_query.setLayout(self.grid_query)

        #Line for the search name, to save
        self.label_name = QtGui.QLabel("Search name : ")
        self.line_name = QtGui.QLineEdit()

        self.line_search_main = QtGui.QLineEdit()
        self.combo_field_main = QtGui.QComboBox()
        self.combo_field_main.addItems(["Topic", "Author(s)"])

        #Button to add a new research field
        self.button_add = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_236_zoom_in'), None, self)
        self.button_add.setToolTip("Add research field")

        #Make more space in the layout for the search name
        self.grid_query.setRowStretch(1, 2)

        #Build the grid
        self.grid_query.addWidget(self.label_name, 0, 0)
        self.grid_query.addWidget(self.line_name, 0, 1, 1, 3)
        self.grid_query.addWidget(self.line_search_main, 2, 0, 1, 3)
        self.grid_query.addWidget(self.combo_field_main, 2, 3)
        self.grid_query.addWidget(self.button_add, 9, 0)

        self.tabs.addTab(self.widget_query, "New query")

##------------------------ ASSEMBLING ------------------------------------------------

        #Create a global vbox, and stack the main widget + the search button
        self.vbox_global = QtGui.QVBoxLayout()
        self.vbox_global.addWidget(self.tabs)

        self.vbox_global.addWidget(self.search_button)

        self.parent.window_search.setLayout(self.vbox_global)
        self.parent.window_search.show()


    #def saveSettings(self):

        #"""Slot to save the settings"""

        #journals_to_parse = []

        #for box in self.check_journals:
            #if box.checkState() == 2:
                #journals_to_parse.append(box.text())

        #if journals_to_parse:
            #self.parent.options.remove("journals_to_parse")
            #self.parent.options.setValue("journals_to_parse", journals_to_parse)
        #else:
            #self.parent.options.remove("journals_to_parse")

        #self.parent.displayTags()
        #self.parent.resetView()

        ##Close the settings window and free the memory
        #self.parent.fen_settings.close()
        #del self.parent.fen_settings
