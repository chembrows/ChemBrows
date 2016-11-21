#!/usr/bin/python
# coding: utf-8

from PyQt5 import QtGui, QtWidgets

class TabPerso(QtWidgets.QTabWidget):

    """Subclassing the TabWidget, to implement the notifications"""

    def __init__(self, parent=None):
        super(TabPerso, self).__init__(parent)


    def setNotifications(self, index, nbr_notifications):

        text = self.tabText(index)

        if nbr_notifications == 0:
            self.setTabText(index, text)
        else:
            self.setTabText(index, "{} ({})".format(text, nbr_notifications))


    def tabText(self, index):

        text = super(TabPerso, self).tabText(index)

        try:
            text = text.split(" (")[0]
        except IndexError:
            pass

        return text
