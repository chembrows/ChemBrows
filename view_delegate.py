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
     

    #def paint(self, painter, option, index):    
        #"""Méthode apppelée case par case pour en dessiner le contenu"""        

        ##Booléens pr la coloration des lignes
        #griser = False
        #yellow = False

        ##On récupère l'option qui détermine si on affiche ou pas
        ##les fichiers qui ne sont pas accessibles
        #display = self.parent.options.value("display_if_missing", True, bool)

        ##On récupère le path du fichier grâce
        ##à la cell de path (invisible).
        #ref_index = index.sibling(index.row(), 4)
        #if not verifAccess(ref_index.data()):
            #if not display:
                ##Si l'option dit qu'on affiche pas les fichiers inaccessibles,
                ##on cache la ligne correspondante et on sort
                #self.parent.tableau.hideRow(index.row())
                #return
            #else:
                ##Si le fichier n'est pas accessible,
                ##on grise
                #griser = True

        ##On récupère la date et on voit si elle est récente
        #ref_index = index.sibling(index.row(), 9)
        #if recent(ref_index.data(), self.parent.options.value("recent", 1, int)):
            ##Si la date est récente, on colorie en jaune
            #yellow = True
        
        ##Index de la miniature
        #if index.column() == 5:
            #path_photo = index.data()

            #if os.path.exists(path_photo):
                ##--- la photo existe: on l'affiche dans la case -------------

                ## on charge la photo dans un QPixmap
                #pixmap = QtGui.QPixmap(path_photo)

                #wcase, hcase = option.rect.width(), option.rect.height()
                #wpix, hpix =  pixmap.width(), pixmap.height()

                ## redim si nécessaire à la taille de la case sans déformation
                #if wpix != wcase or hpix != hcase:
                    #pixmap = pixmap.scaled(wcase, hcase, 
                                             #QtCore.Qt.KeepAspectRatio, 
                                             ##Amélioration de l'image avec smooth
                                             #QtCore.Qt.SmoothTransformation)
                    #wpix, hpix =  pixmap.width(), pixmap.height() # maj

                ## l'affichage se fera au centre de la case sans déformation
                #x = option.rect.x() + (wcase-wpix)//2
                #y = option.rect.y() + (hcase-hpix)//2  

                ## afficher dans le rectagle calculé
                #painter.drawPixmap(QtCore.QRect(x, y, wpix, hpix), pixmap)

            #else:
                ##--- la photo n'existe pas: on met un fond vert -------------
                #painter.fillRect(option.rect, QtGui.QColor("green"))

        ##Si c'est la colonne size, on la formatte pr que ce soit
        ##humainement lisible
        #elif index.column() == 8:
            #size = index.model().data(index)
            #painter.drawText(option.rect, QtCore.Qt.AlignCenter,
                    #str(sizeof(size)))

            ##Si on doit griser
            #if griser:
                ##On colorie le background en gris
                #painter.fillRect(option.rect, QtGui.QColor(100, 100, 100, 90))

            #if yellow:
                ##On colorie le background en jaune
                #painter.fillRect(option.rect, QtGui.QColor(204, 204, 68, 90))

        #else:
            ## on utilise le paint par défaut pour les autres colonnes
            #QtGui.QStyledItemDelegate.paint(self, painter, option, index)    

            #if griser:
                #painter.fillRect(option.rect, QtGui.QColor(100, 100, 100, 75))

            #if yellow:
                #painter.fillRect(option.rect, QtGui.QColor(204, 204, 68, 75))


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
