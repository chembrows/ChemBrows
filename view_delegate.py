#!/usr/bin/python
# -*-coding:Utf-8 -*


"""Module pour modifier le style et la présentation de la vue"""

import sys
import os
from PyQt4 import QtCore, QtGui, QtSql
#from liste import renameFile, verifAccess
#from misc import sizeof, recent


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

        ref_index = index.sibling(index.row(), 11)
        if ref_index.data() == 0:
            red = True
        
        if index.column() == 0:
            pass

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
