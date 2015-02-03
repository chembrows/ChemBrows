#!/usr/bin/python
# -*-coding:Utf-8 -*


"""Module pour modifier les actions de la vue,
ré-implémentations essentiellement"""

from PyQt4 import QtGui, QtCore

from proxy import ProxyPerso

class ViewPerso(QtGui.QTableView):

    def __init__(self, parent=None):
        super(ViewPerso, self).__init__(parent)

        self.parent = parent
        self.defineSlots()

        self.base_query = None


    def defineSlots(self):

        # On connecte le signal de double clic sur une cell vers un
        # slot qui lance le lecteur ac le nom du fichier en paramètre
        self.doubleClicked.connect(self.parent.openInBrowser)

        # http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        # Personal right-click
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.parent.popup)

        self.clicked.connect(self.parent.displayInfos)
        self.clicked.connect(self.parent.displayMosaic)
        self.clicked.connect(self.parent.markOneRead)


    def initUI(self):

        self.horizontal_header = QtGui.QHeaderView(QtCore.Qt.Horizontal) # Déclare le header perso
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignLeft) # Aligne à gauche l'étiquette des colonnes
        self.horizontal_header.setClickable(True)  # Rend cliquable le header perso

        # Resize to content vertically
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # Style du
        self.setHorizontalHeader(self.horizontal_header) # Active le header perso
        self.hideColumn(0)  # Hide id
        self.hideColumn(2)  # Hide doi
        self.hideColumn(6)  # Hide authors
        self.hideColumn(7)  # Hide abstracts
        self.hideColumn(8)  # Hide graphical_abstracts
        self.hideColumn(10)  # Hide urls
        self.hideColumn(11)  # Hide verif
        self.hideColumn(12)  # Hide new
        self.hideColumn(13)  # Hide topic_simple
        # # self.verticalHeader().setDefaultSectionSize(72) # On met la hauteur des cells à la hauteur des thumbs
        # # self.setColumnWidth(5, 127) # On met la largeur de la colonne des thumbs à la largeur des thumbs - 1 pixel (plus joli)
        self.setSortingEnabled(True)  # Active le tri
        self.verticalHeader().setVisible(False)  # Cache le header vertical
        # self.verticalHeader().sectionResizeMode(QHeaderView.ResizeToContents)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)  # Empêche l'édition des cells



    #def currentChanged(self, current, previous):

        #"""Réimplémentation de cette méthode de la vue, pr
        #scroller quand on dépasse les bords de la vue et corriger
        #un bug"""

        #index = current.sibling(current.row(), 4)
        ##Si plusieurs vidéos sont sélectionnées, on arrête les traitements,
        ##cela corrige un bug de double-sélection (issue #79)
        #try:
            #if not index.data() or len(self.parent.vidsSelected()) > 1:
            ##if len(self.parent.vidsSelected()) > 1:
                #return
        #except AttributeError:
            #pass

        ##Scroll sur la dernière ligne visible, pour l'afficher correctement.
        ##De cette manière, en navigant au clavier, si on sort de la zone
        ##d'affichage, on scroll automatiquemet sur la ligne suivante.
        #self.scrollTo(current)


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
        if key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_X:
            current_index = self.selectionModel().currentIndex()

            if not current_index.isValid():
                self.selectRow(0)
                current_index = self.selectionModel().currentIndex()
            else:
                new_index = current_index.sibling(current_index.row() + 1, current_index.column())

                if new_index.isValid():
                    current_index = new_index
                    self.clearSelection()
                    self.setCurrentIndex(current_index)
                    self.clicked.emit(current_index)

        if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_W:
            current_index = self.selectionModel().currentIndex()
            new_index = current_index.sibling(current_index.row() - 1, current_index.column())

            if new_index.isValid():
                current_index = new_index
                self.clearSelection()
                self.setCurrentIndex(current_index)
                self.clicked.emit(current_index)

        #Navigation ac les touches Tab et Ctrl+tab
        if e.modifiers() == QtCore.Qt.ControlModifier:

            #On active le Ctrl+a
            if key == QtCore.Qt.Key_A:
                super(ViewPerso, self).keyPressEvent(e)

        e.ignore()
