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
        self.topic_entries = None
        self.author_entries = None

        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        # Scroll per "pixel". Gives a better impression when scrolling
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)


    def defineSlots(self):

        # Double-click opens in the browser
        self.doubleClicked.connect(self.parent.openInBrowser)

        # http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        # Personal right-click
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.parent.popup)

        self.clicked.connect(self.parent.displayInfos)
        self.clicked.connect(self.parent.displayMosaic)
        self.clicked.connect(self.callParentMarkOneRead)


    def callParentMarkOneRead(self, element):

        """Slot to call the parent method markOneRead.
        The parent method is called through a Timer, which allows (more
        or less) to run the parent method in background. The UI is then
        more fluid"""

        QtCore.QTimer.singleShot(50, lambda: self.parent.markOneRead(element))


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

        # Emit a clicked signal, otherwise the user can like an article
        # while the article is not marked as read
        self.clicked.emit(self.selectionModel().currentIndex())


    def resizeCells(self, new_size):

        """Slot triggered by the parent when the central splitter is moved.
        Allows to resize the columns of the table to optimize space.
        new_size is the width of the central splitter of the parent"""

        row_height = self.rowHeight(0)
        nbr_rows = self.model().rowCount()

        if row_height * nbr_rows > self.height():
            scroll_bar_visible = True
        else:
            scroll_bar_visible = False

        # The thumbnail's size is set to 30 % of the view's width
        size_thumbnail = new_size * 0.3

        # If the scrollbar is not visible (not enough posts), its width
        # is set to 100 px. Weird. So if the scrollBar is not visible,
        # don't substract its size
        if scroll_bar_visible:
            size_title = new_size - size_thumbnail - self.verticalScrollBar().sizeHint().width()
        else:
            size_title = new_size - size_thumbnail

        self.setColumnWidth(8, size_thumbnail)
        self.setColumnWidth(3, size_title)


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
        self.hideColumn(11)  # Hide verif
        self.hideColumn(12)  # Hide new
        self.hideColumn(13)  # Hide topic_simple
        self.horizontalHeader().moveSection(8, 0)  # Move the graphical abstract to first

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)  # No cell editing


    def keyboardSearch(self, search):

        """Reimplementation to deactivate the keyboard search"""

        pass


    def keyPressEvent(self, e):

        """Reaimplementation to propagate the event to the parent
        widget. Also, defines some special behaviors"""

        key = e.key()

        # Browsing with up and down keys. Verifications made for
        # when the selection is completely at the top or the bottom
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

        # if e.modifiers() == QtCore.Qt.ControlModifier:
            # # On active le Ctrl+a
            # if key == QtCore.Qt.Key_A:
                # super(ViewPerso, self).keyPressEvent(e)

        e.ignore()
