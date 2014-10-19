#!/usr/bin/python
# -*-coding:Utf-8 -*


"""Module pour modifier les actions de la vue,
ré-implémentations essentiellement"""

from PyQt4 import QtGui, QtCore

class ViewPerso(QtGui.QTableView):

    def __init__(self, parent=None):
        super(ViewPerso, self).__init__(parent)

        self.parent = parent


    def currentChanged(self, current, previous):

        """Réimplémentation de cette méthode de la vue, pr
        scroller quand on dépasse les bords de la vue et corriger
        un bug"""

        index = current.sibling(current.row(), 4)
        #Si plusieurs vidéos sont sélectionnées, on arrête les traitements,
        #cela corrige un bug de double-sélection (issue #79)
        try:
            if not index.data() or len(self.parent.vidsSelected()) > 1:
            #if len(self.parent.vidsSelected()) > 1:
                return
        except AttributeError:
            pass

        #Scroll sur la dernière ligne visible, pour l'afficher correctement.
        #De cette manière, en navigant au clavier, si on sort de la zone
        #d'affichage, on scroll automatiquemet sur la ligne suivante.
        self.scrollTo(current)


    def keyboardSearch(self, search):

        """Réimplémentation de la méthode, pour désactiver la
        recherche de texte lors de l'appui sur des touches"""

        pass

    def keyPressEvent(self, e):

        """Réimplémentation de la méthode pr que la classe propage
        l'événement au widget parent. L'event n'est pas coincé ici"""

        #super(ViewPerso, self).keyPressEvent(e)

        key = e.key()

        #Navigation parmi les lignes ac les touches haut et bas
        #On fait des vérifications pr que la sélection reste si on est tout
        #en haut ou tout en bas du tableau
        if key == QtCore.Qt.Key_Down:
            current_index = self.selectionModel().currentIndex()

            if not current_index.isValid():
                self.selectRow(0)
                current_index = self.selectionModel().currentIndex()
            else:
                new_index = current_index.sibling(current_index.row() + 1, current_index.column())

                if new_index.isValid():
                    current_index = new_index
                    self.clearSelection()
                else:
                    return

            self.setCurrentIndex(current_index)
            self.clicked.emit(current_index)

        if key == QtCore.Qt.Key_Up:
            current_index = self.selectionModel().currentIndex()
            new_index = current_index.sibling(current_index.row() - 1, current_index.column())

            if new_index.isValid():
                current_index = new_index
                self.clearSelection()
            else:
                return

            self.setCurrentIndex(current_index)
            self.clicked.emit(current_index)

        #Navigation ac les touches Tab et Ctrl+tab
        if e.modifiers() == QtCore.Qt.ControlModifier:
            current_index = self.selectionModel().currentIndex()
            if key == QtCore.Qt.Key_Tab:
                current_index = current_index.sibling(current_index.row() + 1, current_index.column())

                #On checke si le nouvel index est valide, pr ne pas sortir
                #du tableau si on arrive à la fin ou au début
                if current_index.isValid():
                    self.clearSelection()
                    self.setCurrentIndex(current_index)
                    self.clicked.emit(current_index)

            #On active le Ctrl+a
            if key == QtCore.Qt.Key_A:
                super(ViewPerso, self).keyPressEvent(e)

        elif int(e.modifiers()) == QtCore.Qt.ControlModifier + QtCore.Qt.ShiftModifier:
            current_index = self.selectionModel().currentIndex()
            if key == QtCore.Qt.Key_Backtab:
                current_index = current_index.sibling(current_index.row() - 1, current_index.column())

                if current_index.isValid():
                    self.clearSelection()
                    self.setCurrentIndex(current_index)
                    self.clicked.emit(current_index)

        #On ignore l'event, il est propagé au widget parent
        e.ignore()
