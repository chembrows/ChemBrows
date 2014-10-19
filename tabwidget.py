#!/usr/bin/python
# -*-coding:Utf-8 -*

"""Réimplémentation de la classe pour neutraliser la navigation
par Ctrl+Tab entre les onglets"""

from PyQt4 import QtGui

class TabPerso(QtGui.QTabWidget):

    def __init__(self, parent=None):
        super(TabPerso, self).__init__(parent)

    def keyPressEvent(self, e):

        """On ignore tous les events claviers"""

        e.ignore()

#if __name__ == "__main__":
    #pass

