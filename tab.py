#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtGui

class TabPerso(QtGui.QTabWidget):

    """Subclassing the TabWidget, to implement the notifications"""

    def __init__(self, parent=None):
        super(TabPerso, self).__init__(parent)


    def setNotifications(self, index, nbr_notifications):

        if nbr_notifications == 0:
            return

        text = self.tabText(index)
        self.setTabText(index, "{} ({})".format(text, nbr_notifications))


    def tabText(self, index):

        text = super(TabPerso, self).tabText(index)

        return text.split(" (")[0]
