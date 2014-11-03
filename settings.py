#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
from PyQt4 import QtGui, QtCore


class Settings(QtGui.QDialog):

    """Classe pour effectuer les réglages du programme
    par l'utilisateur. On crée une fenêtre secondaire."""

    def __init__(self, parent):

        super(Settings, self).__init__(parent)

        self.parent = parent

        self.urls_to_parse = []
        self.check_journals = []

        self.initUI()
        self.connexion()
        self.etablirSlots()


    def connexion(self):

        """Get the settings and restore them"""

        journals_to_parse = self.parent.options.value("journals_to_parse", [])

        #Check the boxes
        if not journals_to_parse:
            return
        else:
            for box in self.check_journals:
                if box.text() in journals_to_parse:
                    box.setCheckState(2)
                else:
                    box.setCheckState(0)


    def etablirSlots(self):

        """Establish the slots"""

        #To close the window and save the settings
        self.ok_button.clicked.connect(self.saveSettings)


    def selectBrowser(self):

        """Méthode pour retourner le chemin du player"""

        #path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        #self.line_path.setText(path)
        pass


    def initUI(self):

        """Handles the display"""

        self.parent.fen_settings = QtGui.QWidget()
        self.parent.fen_settings.setWindowTitle('Settings')

        self.ok_button = QtGui.QPushButton("OK", self)

        self.grid_settings = QtGui.QGridLayout()

        i = 0
        for company in os.listdir("./journals"):
            with open('journals/{0}'.format(company), 'r') as config:
                for line in config:
                    self.urls_to_parse.append(line.split(" : ")[2])
                    check_box = QtGui.QCheckBox(line.split(" : ")[1])
                    check_box.setCheckState(2)
                    self.check_journals.append(check_box)
                    self.grid_settings.addWidget(check_box, i, 0)
                    i += 1

        self.tabs = QtGui.QTabWidget()

        self.tab_prefs = QtGui.QWidget()
        self.tab_prefs.setLayout(self.grid_settings)
        self.tabs.addTab(self.tab_prefs, "Général")

        self.vbox_global = QtGui.QVBoxLayout()
        self.vbox_global.addWidget(self.tabs)

        self.vbox_global.addWidget(self.ok_button)

        self.parent.fen_settings.setLayout(self.vbox_global)
        self.parent.fen_settings.show()


    def saveSettings(self):

        """Slot to save the settings"""

        journals_to_parse = []

        for box in self.check_journals:
            if box.checkState() == 2:
                journals_to_parse.append(box.text())

        if journals_to_parse:
            self.parent.options.remove("journals_to_parse")
            self.parent.options.setValue("journals_to_parse", journals_to_parse)
        else:
            self.parent.options.remove("journals_to_parse")

        #On ferme la fenêtre et on libère la mémoire
        self.parent.fen_settings.close()
        del self.parent.fen_settings
