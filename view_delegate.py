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
        ref_index = index.sibling(index.row(), 11)
        if ref_index.data() == 0:
            red = True

        #If the post is new, set font to bold
        new = index.sibling(index.row(), 12).data()
        if new == 1:
            option.font.setWeight(QtGui.QFont.Bold)

        date = index.sibling(index.row(), 4).data()
        
        #Condition block to perform actions on specific columns
        #if index.column() == 0:
            #pass

        if index.column() == 1:

            percentage = index.model().data(index)
            if new == 1:
                option.font.setWeight(QtGui.QFont.Bold)

            if type(percentage) is float:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(int(round(percentage, 0))))
            else:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(0))

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))


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



    #def createEditor(self, parent, option, index):

        #"""On redéfinit la méthode createEditor du delegate, pour pouvoir
        #connecter la fin de l'édition à la fonction qui renommera physiquement
        #le fichier"""

        ##On crée une QLineEdit, avec pour parent la cell qui appelle cette
        ##méthode
        #edition = QtGui.QLineEdit(index.data(), parent)

        ##On connecte la Line avec la fct de renommage, du fichier liste
        ##Obligé d'utiliser une lambda, sinon la fct renvoyait un NoneType
        ##http://stackoverflow.com/questions/10730131/create-dynamic-button-in-pyqt
        #edition.returnPressed.connect(lambda: renameFile(index.data(), edition.text(), self.parent.bdd))
        #edition.returnPressed.connect(self.afterRename)

        #return edition


    #def afterRename(self):

        #"""Méthode qui corrige un bug de modèle lors du
        #renommage des fichiers"""

        #self.parent.modele.setTable("videos")
        #self.parent.modele.select()
        #self.parent.adjustView()


    #def setModelData(self, editor, model, index):

        #"""On redéfinit cette fct pr ne pas qu'elle court-circuite
        #la fct createEditor redéfinie, sinon cette fct écrit en bdd le nom du
        #fichier directement, sans vérification"""

        #try:
            #model.sourceModel().setQuery(self.parent.query)
        #except AttributeError:
            #model.sourceModel().select()
