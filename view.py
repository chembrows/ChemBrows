#!/usr/bin/python
# coding: utf-8


from PyQt5 import QtGui, QtWidgets, QtCore


class ViewPerso(QtWidgets.QTableView):

    """New class to modify the view. Basically reimplements some methods.
    Generates a personnal table view, which will be used for each tab in the
    main window"""

    def __init__(self, parent=None):

        super(ViewPerso, self).__init__(parent)

        self.parent = parent
        self.defineSlots()

        self.name_search = None
        self.base_query = None
        self.topic_entries = None
        self.author_entries = None
        self.radio_states = None
        self.articles = {}

        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Scroll per "pixel". Gives a better impression when scrolling
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)


    def defineSlots(self):

        # Double-click opens in the browser
        self.doubleClicked.connect(self.parent.openInBrowser)

        # http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        # Personal right-click
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.parent.popup)

        self.clicked.connect(self.parent.displayInfos)
        self.clicked.connect(self.parent.markOneRead)


    def mousePressEvent(self, e):

        """Adding some actions to the normal mousePressEvent.
        Determine if the user clicked in the right bottom corner.
        If yes, the user clicked on the 'like star', so the liked
        state is toggled from the parent toggleLike method"""

        # Constant to set the size of the zone in the bottom right
        # corner, where the user can click to toggle liked state
        DIMENSION = self.parent.styles.ICON_SIZE_SMALL

        # Attribute to shunt parent.markOneRead if the user is clicking
        # on the read/unread icon
        self.toread_icon = False

        # Call the parent class function
        super(ViewPerso, self).mousePressEvent(e)

        # Get the current cell as a QRect
        rect = self.visualRect(self.selectionModel().currentIndex())

        # Get the coordinates of the mouse click
        x, y = e.x(), e.y()

        # area_y: to check if the click is in the bottom part of the post
        # area_*_x: to check if the click is on the to-read icon,
        # or the like icon
        area_like_x, area_wait_x, area_y = False, False, False

        # If the click was on the right bottom corner, start the real buisness
        if y <= rect.y() + rect.height() and y >= rect.y() + rect.height() - DIMENSION:
            area_y = True
        if x <= rect.x() + rect.width() and x >= rect.x() + rect.width() - DIMENSION:
            area_like_x = True
        if x >= rect.x() + rect.width() - 2 * DIMENSION and x <= rect.x() + rect.width() - DIMENSION:
            area_wait_x = True

        if area_like_x and area_y:
            self.parent.toggleLike()

            # Emit a clicked signal, otherwise the user can like an article
            # while the article is not marked as read
            self.clicked.emit(self.selectionModel().currentIndex())

        # Icon to-read
        elif area_wait_x and area_y:
            self.toread_icon = True
            self.parent.toggleWait()


    def updateHeight(self):

        self.verticalHeader().setDefaultSectionSize(self.height() * 0.17)


    def resizeCells(self, new_size):

        """Slot triggered by the parent when the central splitter is moved.
        Allows to resize the columns of the table to optimize space.
        new_size is the width of the central splitter of the parent"""

        # The thumbnail's size is set to 30 % of the view's width
        # The rest is filled with the stretchable title
        self.setColumnWidth(8, new_size * 0.3)


    def initUI(self):

        # Turn off the horizontal scrollBar. Not necessary, and ugly
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Header style
        self.hideColumn(0)  # Hide id
        self.hideColumn(1)  # Hide percentage match
        self.hideColumn(2)  # Hide doi
        self.hideColumn(4)  # Hide date
        self.hideColumn(5)  # Hide journals
        self.hideColumn(6)  # Hide authors
        self.hideColumn(7)  # Hide abstracts
        self.hideColumn(9)  # Hide like
        self.hideColumn(10)  # Hide urls
        self.hideColumn(11)  # Hide new
        self.hideColumn(12)  # Hide topic_simple
        self.hideColumn(13)  # Hide author_simple

        # Stretch the title into the remaining space
        self.horizontalHeader().setSectionResizeMode(3,
            QtWidgets.QHeaderView.Stretch)

        # Move the graphical abstract to first
        self.horizontalHeader().moveSection(8, 0)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)

        # No cell editing
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    def keyboardSearch(self, search):

        """Reimplementation to deactivate the keyboard search"""

        pass


    def keyPressEvent(self, e):

        """Reimplementation to propagate the event to the parent
        widget. Also, defines some special behaviors"""

        # super(ViewPerso, self).keyPressEvent(e)

        key = e.key()

        # To avoid a bug: the user scrolls the articles w/ the keyboard,
        # put an article in the toread list, and then continues scrolling.
        # The posts are not marked as read anymore
        if key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Up:
            self.toread_icon = False

        # Browsing with up and down keys. Verifications made for
        # when the selection is completely at the top or the bottom
        if key == QtCore.Qt.Key_Down:
            current_index = self.selectionModel().currentIndex()

            if not current_index.isValid():
                self.selectRow(0)
                current_index = self.selectionModel().currentIndex()
            else:
                new_index = current_index.sibling(current_index.row() + 1, current_index.column())

                if new_index.isValid():
                    current_index = new_index
                    self.setCurrentIndex(current_index)
                    self.clicked.emit(current_index)

        if key == QtCore.Qt.Key_Up:
            current_index = self.selectionModel().currentIndex()
            new_index = current_index.sibling(current_index.row() - 1, current_index.column())

            if new_index.isValid():
                current_index = new_index
                self.setCurrentIndex(current_index)
                self.clicked.emit(current_index)

        e.ignore()
