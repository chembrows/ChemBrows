#!/usr/bin/python
# -*-coding:Utf-8 -*


"""Module pour modifier le style et la présentation de la vue"""

import sys
import os
from PyQt4 import QtCore, QtGui, QtSql

from functions import prettyDate


class ViewDelegate(QtGui.QStyledItemDelegate):

    """Delegate perso pour afficher des miniatures dans
    un QTableView
    http://www.siteduzero.com/forum-83-812350-p1-pyqt-inserer-des-images-dans-un-qtableview.html#r7783319"""
     

    def __init__(self, parent):

        super(ViewDelegate, self).__init__(parent)

        self.parent = parent
     

    def paint(self, painter, option, index):    

        """Method called to draw the content of the cells"""        

        #Bool to color lines
        red = False

        #If the data are not complete (i.e 'verif' is False), color red
        verif = index.sibling(index.row(), 11).data()
        if verif == 0:
            red = True

        #If the post is new, set font to bold
        new = index.sibling(index.row(), 12).data()
        font = painter.font()
        if new == 1:
            Set the font to bold w/ 2 different ways.
            #One for the default painter, and one for the custom painter
            option.font.setWeight(QtGui.QFont.Bold)
            font.setBold(True)
        else:
            font.setBold(False)
        painter.setFont(font)

        date = index.sibling(index.row(), 4).data()
        
        #Condition block to perform actions on specific columns
        if index.column() == 1:

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))

            percentage = index.model().data(index)

            if type(percentage) is float:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(int(round(percentage, 0))))
            else:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(0))

        #Actions on the date
        elif index.column() == 4:

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))

            painter.drawText(option.rect, QtCore.Qt.AlignCenter, prettyDate(date))


        else:
            #Using default painter
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)    

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))
