#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtGui, QtCore


class ViewPerso(QtGui.QTableView):

    """New class to modify the view. Basically reimplements some methods.
    Generates a personnal table view, which will be used for each tab in the
    main window"""


    def __init__(self, parent=None):
        super(ViewPerso, self).__init__(parent)

        self.parent = parent
        self.defineSlots()

        self.base_query = None

        # Scroll per "pixel". Gives a better impression when scrolling
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)


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


    def mousePressEvent(self, e):

        """Adding some action to the normal mousePressEvent.
        Determine if the user clicked in the right bottom corner.
        If yes, the user clicked on the 'like star', so the liked
        state is toggled from the parent toggleLike method"""

        # Constant to set the size of the zone in the bottom right
        # corner, where the user can click to toggle liked state
        DIMENSION = 25

        # Call the parent class function
        super(ViewPerso, self).mousePressEvent(e)

        # Get the current cell as a QRect
        rect = self.visualRect(self.selectionModel().currentIndex())

        # Get the x and y coordinates of the mouse click
        x = e.x()
        y = e.y()

        corner_x, corner_y = False, False

        # If the click was on the right bottom corner, start the real buisness
        if x <= rect.x() + rect.width() and x >= rect.x() + rect.width() - DIMENSION:
            corner_x = True
        if y <= rect.y() + rect.height() and y >= rect.y() + rect.height() - DIMENSION:
            corner_y = True

        if corner_x and corner_y:
            self.parent.toggleLike()


    def initUI(self):

        self.horizontal_header = QtGui.QHeaderView(QtCore.Qt.Horizontal)  # Déclare le header perso
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignLeft)  # Aligne à gauche l'étiquette des colonnes
        self.horizontal_header.setClickable(True)  # Rend cliquable le header perso

        # Resize to content vertically
        # self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # Header style
        self.setHorizontalHeader(self.horizontal_header)  # Active le header perso
        self.hideColumn(0)  # Hide id
        self.hideColumn(2)  # Hide doi
        self.hideColumn(6)  # Hide authors
        self.hideColumn(7)  # Hide abstracts
        self.hideColumn(9)  # Hide like
        self.hideColumn(10)  # Hide urls
        self.hideColumn(11)  # Hide verif
        self.hideColumn(12)  # Hide new
        self.hideColumn(13)  # Hide topic_simple
        self.horizontalHeader().moveSection(8, 0)  # Move the graphical abstract to first
        self.horizontalHeader().moveSection(2, 8)  # Move percentage match at the end
        self.verticalHeader().setDefaultSectionSize(200)
        self.setColumnWidth(8, 200)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        # self.verticalHeader().sectionResizeMode(QHeaderView.ResizeToContents)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)  # Empêche l'édition des cells


    def keyboardSearch(self, search):

        """Réimplémentation de la méthode, pour désactiver la
        recherche de texte lors de l'appui sur des touches"""

        pass

    def keyPressEvent(self, e):

        """Réimplémentation de la méthode pr que la classe propage
        l'événement au widget parent. L'event n'est pas coincé ici"""

        # super(ViewPerso, self).keyPressEvent(e)

        key = e.key()

        # Navigation parmi les lignes ac les touches haut et bas
        # On fait des vérifications pr que la sélection reste si on est tout
        # en haut ou tout en bas du tableau
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

        # Navigation ac les touches Tab et Ctrl+tab
        if e.modifiers() == QtCore.Qt.ControlModifier:

            # On active le Ctrl+a
            if key == QtCore.Qt.Key_A:
                super(ViewPerso, self).keyPressEvent(e)

        e.ignore()
