#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import signal
import subprocess

from PyQt4 import QtGui, QtSql, QtCore, QtWebKit

import fnmatch

# DEBUG
import datetime
import webbrowser

# Personal modules
from log import MyLog
from model import ModelPerso
from view import ViewPerso
from graphicsview import GraphicsViewPerso
from view_delegate import ViewDelegate
from worker import Worker
from predictor import Predictor
from settings import Settings
from advanced_search import AdvancedSearch
# from proxy import ProxyPerso
import functions



class Fenetre(QtGui.QMainWindow):

    def __init__(self):

        super(Fenetre, self).__init__()

        self.l = MyLog()
        self.l.info('Starting the program')

        # Set the logging level to Error (debugging)
        self.l.setLevel(20)

        # Object to store options and preferences
        self.options = QtCore.QSettings("options.ini", QtCore.QSettings.IniFormat)

        QtGui.qApp.installEventFilter(self)

        # List to store the tags checked
        self.tags_selected = []

        # List to store all the views, models and proxies
        self.liste_tables_in_tabs = []
        self.liste_models_in_tabs = []
        self.liste_proxies_in_tabs = []

        self.connectionBdd()
        self.defineActions()
        self.initUI()
        self.defineSlots()
        self.displayTags()
        self.restoreSettings()


    def connectionBdd(self):

        """Method to connect to the database. Creates it
        if it does not exist"""

        # Set the database
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName("fichiers.sqlite")

        self.bdd.open()

        query = QtSql.QSqlQuery(self.bdd)
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                     doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                     liked INTEGER, url TEXT, verif INTEGER, new INTEGER, topic_simple TEXT)")


    def getJournalsToCare(self):

        """Get the journals checked in the settings window"""

        # Create a list to store the journals checked in the settings window
        journals = self.options.value("journals_to_parse", [])

        # If no journals to care in the settings,
        # take them all. So build a journals_to_care list
        # with all the journals
        if not journals:
            # self.journals_to_care = []
            for company in os.listdir("./journals"):
                with open('journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        # Take the abbreviation
                        journals.append(line.split(" : ")[1])

        return journals


    def parse(self):

        """Method to start the parsing of the data"""

        journals_to_parse = self.options.value("journals_to_parse", [])

        # If no journals to parse in the settings,
        # parse them all. So build a journals_to_parse list
        # with all the journals
        if not journals_to_parse:
            journals_to_parse = []
            for company in os.listdir("./journals"):
                with open('journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        journals_to_parse.append(line.split(" : ")[1])

            self.options.remove("journals_to_parse")
            self.options.setValue("journals_to_parse", journals_to_parse)

        urls = []
        for company in os.listdir("./journals"):
            with open('journals/{0}'.format(company), 'r') as config:
                for line in config:
                    if line.split(" : ")[1] in journals_to_parse:
                        urls.append(line.split(" : ")[2])

        # Disabling the parse action to avoid double start
        self.parseAction.setEnabled(False)

        # List to store the threads.
        # The list is cleared when the method is started
        self.list_threads = []

        self.start_time = datetime.datetime.now()

        for site in urls:
            # One worker for each website
            worker = Worker(site, self.l, self.bdd)
            self.list_threads.append(worker)
            worker.finished.connect(self.checkThreads)

        # Get the optimal nbr of thread. Will vary depending
        # on the user's computer
        # max_nbr_threads = QtCore.QThread.idealThreadCount()

        # Start a certain nbr of threads
        # for worker in self.list_threads[:max_nbr_threads]:
        for worker in self.list_threads[:2]:
            self.l.info("New thread started")
            worker.start()


    def checkThreads(self):

        """Method to check the state of each thread.
        If all the threads are finished, enable the parse action.
        This slot is called when a thread is finished, to start the
        next one"""

        elsapsed_time = datetime.datetime.now() - self.start_time
        self.l.info(elsapsed_time)

        # Get a list of the workers states
        list_states = [worker.isFinished() for worker in self.list_threads]

        # Print the nbr of finished threads
        self.l.info("Finis: {}/{}".format(list_states.count(True), len(self.list_threads)))

        if False not in list_states:
            self.calculatePercentageMatch()
            self.parseAction.setEnabled(True)
            self.l.debug("Parsing data finished. Enabling parseAction")

            # Update the view when a worker is finished
            self.updateView()
        else:
            self.l.info("STARTING NEW THREAD")
            # self.updateView()
            for worker in self.list_threads:
                if not worker.isRunning() and not worker.isFinished():
                    worker.start()
                    break


    def defineActions(self):

        """On définit ici les actions du programme. Cette méthode est
        appelée à la création de la classe"""

        # Action to quit
        self.exitAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_063_power'), '&Quitter', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Quit")
        self.exitAction.triggered.connect(self.closeEvent)

        # Action to refresh the posts
        self.parseAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_081_refresh.png'), '&Refresh', self)
        self.parseAction.setShortcut('F5')
        self.parseAction.setStatusTip("Download new posts")
        self.parseAction.triggered.connect(self.parse)

        # Action to calculate the percentages of match
        self.calculatePercentageMatchAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_040_stats.png'), '&Percentages', self)
        self.calculatePercentageMatchAction.setShortcut('F6')
        self.calculatePercentageMatchAction.setStatusTip("Calculate percentages")
        self.calculatePercentageMatchAction.triggered.connect(self.calculatePercentageMatch)

        # Action to like a post
        self.toggleLikeAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_343_thumbs_up'), 'Toggle Like for the post', self)
        self.toggleLikeAction.setShortcut('L')
        self.toggleLikeAction.triggered.connect(self.toggleLike)

        # Action to open the post in browser
        self.openInBrowserAction = QtGui.QAction('Open post in browser', self)
        self.openInBrowserAction.triggered.connect(self.openInBrowser)
        self.openInBrowserAction.setShortcut('Ctrl+W')

        # Action to update the model. For TEST
        self.updateAction = QtGui.QAction('Update model', self)
        self.updateAction.triggered.connect(self.updateModel)
        self.updateAction.setShortcut('F7')

        # Action to show a settings window
        self.settingsAction = QtGui.QAction('Preferences', self)
        self.settingsAction.triggered.connect(lambda: Settings(self))

        # Action so show new articles
        self.searchNewAction = QtGui.QAction('Unread', self)
        self.searchNewAction.triggered.connect(self.searchNew)

        # Action to toggle the read state of an article
        self.toggleReadAction = QtGui.QAction('Toggle read state', self)
        self.toggleReadAction.setShortcut('M')
        self.toggleReadAction.triggered.connect(self.toggleRead)

        # Start the search
        self.searchAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_027_search'), 'Search', self)
        self.searchAction.triggered.connect(self.research)

        # Start advanced search
        self.advanced_searchAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_025_binoculars'), 'Advanced search', self)
        self.advanced_searchAction.triggered.connect(lambda: AdvancedSearch(self))

        # Action to change the sorting method of the views
        self.sortingPercentageAction = QtGui.QAction('By percentage match', self, checkable=True)
        self.sortingPercentageAction.triggered.connect(lambda: self.changeSortingMethod(1,
                                                                                        reverse=self.sortingReversedAction.isChecked()))
        # Action to change the sorting method of the views
        self.sortingDateAction = QtGui.QAction('By date', self, checkable=True)
        self.sortingDateAction.triggered.connect(lambda: self.changeSortingMethod(4,
                                                                                  reverse=self.sortingReversedAction.isChecked()))
        # Action to change the sorting method of the views, reverse the results
        self.sortingReversedAction = QtGui.QAction('Reverse order', self, checkable=True)
        self.sortingReversedAction.triggered.connect(lambda: self.changeSortingMethod(self.sorting_method,
                                                                                      reverse=self.sortingReversedAction.isChecked()))
        # Action to serve use as a separator
        self.separatorAction = QtGui.QAction(self)
        self.separatorAction.setSeparator(True)


    def changeSortingMethod(self, method_nbr, reverse):

        """
        Slot to change the sorting method of the
        articles. Get an int as a parameter:
        1 -> percentage match
        4 -> date
        reverse -> if True, descending order
        """

        # Set a class attribute, to save with the QSettings,
        # to restore the check at boot
        self.sorting_method = method_nbr
        self.sorting_reversed = reverse

        if self.sorting_method == 1:
            self.sortingPercentageAction.setChecked(True)
            self.sortingDateAction.setChecked(False)
        elif self.sorting_method == 4:
            self.sortingPercentageAction.setChecked(False)
            self.sortingDateAction.setChecked(True)

        if self.sorting_reversed:
            self.sortingReversedAction.setChecked(True)
        else:
            self.sortingReversedAction.setChecked(False)

        for table in self.liste_tables_in_tabs:
            # Qt.AscendingOrder   0   starts with 'AAA' ends with 'ZZZ'
            # Qt.DescendingOrder  1   starts with 'ZZZ' ends with 'AAA'
            # if "reverse order" in unchecked, reverse = False = 0
            # -> 1 - reverse = 1 -> DescendingOrder -> starts with the
            # highest percentages
            table.sortByColumn(method_nbr, 1 - reverse)


    def updateModel(self):

        """Debug function, allows to update a model
        with a button, at any time. Will not be used by
        the final user"""

        self.updateView()


    def closeEvent(self, event):

        """Méthode pr effetcuer des actions avant de
        quitter, comme sauver les options dans un fichier
        de conf"""

        # http://stackoverflow.com/questions/9249500/
        # pyside-pyqt-detect-if-user-trying-to-close-window

        # Record the window state and appearance
        self.options.beginGroup("Window")

        # Reinitializing the keys
        self.options.remove("")

        self.l.debug("Sauvegarde de l'état de la fenêtre dans options.ini")
        self.options.setValue("window_geometry", self.saveGeometry())
        self.options.setValue("window_state", self.saveState())

        for index, each_table in enumerate(self.liste_tables_in_tabs):
            self.options.setValue("header_state{0}".format(index), each_table.horizontalHeader().saveState())

        # Save the states of the splitters of the window
        self.options.setValue("central_splitter", self.splitter1.saveState())
        self.options.setValue("final_splitter", self.splitter2.saveState())

        # Save the sorting method
        try:
            self.options.setValue("sorting_method", self.sorting_method)
        except AttributeError:
            self.options.setValue("sorting_method", 1)
        try:
            self.options.setValue("sorting_reversed", self.sorting_reversed)
        except AttributeError:
            self.options.setValue("sorting_reversed", False)

        # Save the checked journals (on the left)
        if self.tags_selected and self.tags_selected != self.getJournalsToCare():
            self.options.setValue("tags_selected", self.tags_selected)

        self.options.endGroup()

        # Be sure self.options finished its tasks.
        # Correct a bug
        self.options.sync()

        # Close the database connection
        self.bdd.removeDatabase("fichiers.sqlite")
        self.bdd.close()

        QtGui.qApp.quit()

        self.l.info("Closing the program")


    def restoreSettings(self):

        """Restore the prefs of the window"""

        searches_saved = QtCore.QSettings("searches.ini", QtCore.QSettings.IniFormat)

        # Restore the saved searches
        for search_name in searches_saved.childGroups():
            query = searches_saved.value("{0}/sql_query".format(search_name))
            topic_entries = searches_saved.value("{0}/topic_entries".format(search_name), None)
            author_entries = searches_saved.value("{0}/author_entries".format(search_name), None)
            self.createSearchTab(search_name, query,
                                 topic_options=topic_entries,
                                 author_options=author_entries)

        # Si des réglages pour la fenêtre
        # sont disponibles, on les importe et applique
        if "Window" in self.options.childGroups():

            self.restoreGeometry(self.options.value("Window/window_geometry"))
            self.restoreState(self.options.value("Window/window_state"))

            for index, each_table in enumerate(self.liste_tables_in_tabs):
                header_state = self.options.value("Window/header_state{0}".format(index))
                if header_state is not None:
                    each_table.horizontalHeader().restoreState(self.options.value("Window/header_state{0}".format(index)))

            self.splitter1.restoreState(self.options.value("Window/central_splitter"))
            self.splitter2.restoreState(self.options.value("Window/final_splitter"))

            # # Bloc to restore the check of the sorting method, in the View menu
            # # of the menubar
            self.sorting_method = self.options.value("Window/sorting_method", 1, int)
            self.sorting_reversed = self.options.value("Window/sorting_reversed", False, bool)

            # Restore the journals selected (buttons pushed)
            self.tags_selected = self.options.value("Window/tags_selected", [])
            if self.tags_selected == self.getJournalsToCare():
                self.tags_selected = []
            if self.tags_selected:
                for button in self.list_buttons_tags:
                    if button.text() in self.tags_selected:
                        button.setChecked(True)

        try:
            self.changeSortingMethod(self.sorting_method, self.sorting_reversed)
        except AttributeError:
            self.changeSortingMethod(1, False)

        self.getJournalsToCare()

        self.searchByButton()

        # Change the height of the rows
        for table in self.liste_tables_in_tabs:
            table.verticalHeader().setDefaultSectionSize(table.height() * 0.2)

        # Timer to get the dimensions of the window right.
        # If the window is displayed too fast, I can't get the dimensions right
        QtCore.QTimer.singleShot(50, self.updateCellSize)


    def eventFilter(self, source, event):

        """Sublclassing of this method allows to hide/show
        the journals filters on the left, through a mouse hover event"""

        # do not hide menubar when menu shown
        if QtGui.qApp.activePopupWidget() is None:
            if event.type() == QtCore.QEvent.MouseMove:
                if self.scroll_tags.isHidden():
                    try:
                        # Calculate the top zone where resizing can't happen (menubar, toolbar, etc)
                        table_y = self.toolbar.rect().height() + self.menubar.rect().height() + \
                                self.mapToGlobal(QtCore.QPoint(0, 0)).y() + self.hbox_central.getContentsMargins()[1]
                    except AttributeError:
                        pass
                    rect = self.geometry()
                    rect.setWidth(25)
                    rect.setTop(table_y)
                    if rect.contains(event.globalPos()):
                        self.scroll_tags.show()
                else:
                    width_layout = self.hbox_central.getContentsMargins()[2]
                    rect = QtCore.QRect(
                        self.scroll_tags.mapToGlobal(QtCore.QPoint(-width_layout, 0)),
                        self.scroll_tags.size())
                    if not rect.contains(event.globalPos()):
                        self.scroll_tags.hide()
                        # Give enough time to the program to get new splitter size,
                        # before resizing the cells
                        QtCore.QTimer.singleShot(20, self.updateCellSize)

            elif event.type() == QtCore.QEvent.Leave and source is self:
                self.scroll_tags.hide()
                self.updateCellSize()

        return QtGui.QMainWindow.eventFilter(self, source, event)


    def resizeEvent(self, event):

        """Called when the Main window is resized.
        Reimplemented to resize the cell when the window
        is resized"""

        super(Fenetre, self).resizeEvent(event)

        QtCore.QTimer.singleShot(30, self.updateCellSize)


    def popup(self, pos):

        """Method to handle right-click"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        if not table.selectionModel().selection().indexes():
            return
        else:
            self.displayInfos()
            self.displayMosaic()

        # Define a new postition for the menu
        new_pos = QtCore.QPoint(pos.x() + 240, pos.y() + 120)

        # Create the right-click menu and add the actions
        menu = QtGui.QMenu()
        menu.addAction(self.toggleReadAction)
        menu.addAction(self.toggleLikeAction)
        menu.addAction(self.openInBrowserAction)

        menu.exec_(self.mapToGlobal(new_pos))


    def defineSlots(self):

        """Connect the slots"""

        # Connect the back button
        self.button_back.clicked.connect(self.resetView)

        # Launch the research if Enter pressed
        self.research_bar.returnPressed.connect(self.research)

        # Perform some stuff when the tab is changed
        self.onglets.currentChanged.connect(self.tabChanged)

        # When the central splitter is moved, perform some actions,
        # like resizing the cells of the table
        self.splitter2.splitterMoved.connect(self.updateCellSize)


    def updateCellSize(self):

        """Update the cell size when the user moves the central splitter.
        For a better display"""

        # Get the size of the main splitter
        new_size = self.splitter2.sizes()[0]

        self.liste_tables_in_tabs[self.onglets.currentIndex()].resizeCells(new_size)

        for table in self.liste_tables_in_tabs:
            table.verticalHeader().setDefaultSectionSize(table.height() * 0.2)


    def displayInfos(self):

        """Method to get the infos of a post.
        For now, gets only the abstract"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 7).data()
        title = table.model().index(table.selectionModel().selection().indexes()[0].row(), 3).data()
        author = table.model().index(table.selectionModel().selection().indexes()[0].row(), 6).data()
        date = table.model().index(table.selectionModel().selection().indexes()[0].row(), 4).data()

        self.label_date.setText(date)
        self.label_title.setText("<span style='font-size:12pt; font-weight:bold'>{0}</span>".format(title))

        if type(abstract) == str:
            self.text_abstract.setHtml(table.model().index(table.selectionModel().selection().indexes()[0].row(), 7).data())
        else:
            self.text_abstract.setHtml("")

        if type(author) == str:
            self.label_author.setText(author)
        else:
            self.label_author.setText("")


    def displayMosaic(self):

        """Slot qui affiche la mosaïque de la vidéo dans
        la partie droite"""
        # infos:
        # http://vincent-vande-vyvre.developpez.com/tutoriels/pyqt/manipulation-images/

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        try:
            path_graphical_abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 8).data()
            if type(path_graphical_abstract) is not str:
                try:
                    self.scene.clear()
                except AttributeError:
                    self.l.warn("No scene object yet, displayMosaic")
                return
        except TypeError:
            self.l.debug("No graphical abstract for this post, displayMosaic()")
            self.scene.clear()
            return

        # Get the path of the graphical abstract
        path_graphical_abstract = "./graphical_abstracts/" + path_graphical_abstract

        w_vue, h_vue = self.vision.width(), self.vision.height()
        self.current_image = QtGui.QImage(path_graphical_abstract)

        # Scale the picture
        self.pixmap = QtGui.QPixmap.fromImage(self.current_image.scaled(w_vue, h_vue,
                                              QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        w_pix, h_pix = self.pixmap.width(), self.pixmap.height()

        self.scene = QtGui.QGraphicsScene()

        # Center the picture
        self.scene.setSceneRect(0, 0, w_pix, h_pix - 10)
        self.scene.addPixmap(self.pixmap)
        self.vision.setScene(self.scene)


    def tabChanged(self):

        """Slot to perform some actions when the current tab is changed.
        Mainly sets the tab query to the saved query"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery(self.bdd)
        self.query.prepare(self.refineBaseQuery(table))
        self.query.exec_()

        table.clearSelection()

        self.updateView()

        for table in self.liste_tables_in_tabs:
            table.verticalHeader().setDefaultSectionSize(table.height() * 0.2)

        # Update the size of the columns of the view if the central
        # splitter moved
        self.updateCellSize()



    def createSearchTab(self, name_search, query, topic_options=None, author_options=None, update=False):

        """Slot called from AdvancedSearch, when a new search is added,
        or a previous one updated"""

        # If the tab's query is updated from the advancedSearch window,
        # just update the base_query
        if update:
            for index in range(self.onglets.count()):
                if name_search == self.onglets.tabText(index):
                    self.liste_tables_in_tabs[index].base_query = query

                    self.liste_tables_in_tabs[index].topic_entries = topic_options
                    self.liste_tables_in_tabs[index].author_entries = author_options

                    if self.onglets.tabText(self.onglets.currentIndex()) == name_search:
                        # Update the view
                        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
                        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
                        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
                        # model.setQuery(table.base_query)
                        model.setQuery(self.refineBaseQuery(table))
                        proxy.setSourceModel(model)
                        table.setModel(proxy)
                    return

        # Create the model for the new tab
        modele = ModelPerso()

        # Changes are effective immediately
        modele.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        modele.setTable("papers")
        modele.select()

        self.liste_models_in_tabs.append(modele)

        proxy = QtGui.QSortFilterProxyModel()
        proxy.setDynamicSortFilter(True)
        proxy.setSourceModel(modele)
        self.liste_proxies_in_tabs.append(proxy)

        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.base_query = query
        tableau.topic_entries = topic_options
        tableau.author_entries = author_options
        tableau.setModel(proxy)
        tableau.setItemDelegate(ViewDelegate(self))
        tableau.setSelectionBehavior(tableau.SelectRows)
        tableau.initUI()

        self.liste_tables_in_tabs.append(tableau)

        self.onglets.addTab(tableau, name_search)


    def displayTags(self):

        """Slot to display push buttons on the left.
        One button per journal. Only display the journals
        selected in the settings window"""

        self.clearLayout(self.vbox_all_tags)

        self.list_buttons_tags = []

        journals_to_care = self.getJournalsToCare()
        journals_to_care.sort()

        size = 0

        for journal in journals_to_care:

            button = QtGui.QPushButton(journal)
            button.setCheckable(True)
            button.adjustSize()

            if button.width() > size:
                size = button.width()

            button.clicked[bool].connect(self.stateButtons)
            self.vbox_all_tags.addWidget(button)

            self.list_buttons_tags.append(button)

        self.vbox_all_tags.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_tags.setWidget(self.scrolling_tags)
        add = self.vbox_all_tags.getContentsMargins()[0] * 2 + 2 + \
            self.scroll_tags.verticalScrollBar().sizeHint().width()
        self.scroll_tags.setFixedWidth(size + add)


    def stateButtons(self, pressed):

        """Slot to check the journals push buttons"""

        if self.tags_selected == self.getJournalsToCare():
            self.tags_selected = []

        # Get the button pressed
        source = self.sender()

        # Build the list of ON buttons
        if source.parent() == self.scrolling_tags:
            if pressed:
                self.tags_selected.append(source.text())
            else:
                self.tags_selected.remove(source.text())

        self.searchByButton()


    def searchByButton(self):

        """Slot to select articles by journal"""

        # Reset the view when the last button is unchecked
        if not self.tags_selected:
            self.resetView()
            return

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery(self.bdd)

        refined_query = self.refineBaseQuery(table)

        if "WHERE" in refined_query:
            requete = refined_query.replace("WHERE ", "WHERE (")
            requete += ") AND journal IN ("
        else:
            requete = refined_query + " WHERE journal IN ("

        # Building the query
        for each_journal in self.tags_selected:
            if each_journal is not self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            # Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(requete)
        self.query.exec_()

        self.updateView()


    def searchNew(self):

        """Slot to select new articles"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery(self.bdd)

        # First, search the new articles id
        self.query.prepare("SELECT id FROM papers WHERE new=1")
        self.query.exec_()

        list_id = []

        while self.query.next():
            record = self.query.record()
            list_id.append(record.value('id'))

        refined_query = self.refineBaseQuery(table)

        if "WHERE" in refined_query:
            requete = " AND id IN ("
        else:
            requete = " WHERE id IN ("

        # Building the query
        for each_id in list_id:
            if each_id is not list_id[-1]:
                requete = requete + str(each_id) + ", "
            # Close the query if last
            else:
                requete = requete + str(each_id) + ")"

        self.query.prepare(refined_query + requete)
        self.query.exec_()

        self.updateView()


    def refineBaseQuery(self, table):

        """Method to refine the base_query of a view.
        A normal SQL query can't search a comma-separated list, so
        the results of the SQL query are filtered afterwords"""

        author_entries = table.author_entries

        # If no * in the SQL query, return
        if author_entries is None or not any('*' in element for element in author_entries):
            return table.base_query

        query = QtSql.QSqlQuery(self.bdd)
        query.prepare(table.base_query)
        query.exec_()

        # Prepare a list to store the filtered items
        list_ids = []

        while query.next():
            record = query.record()

            # Normalize the authors string of the item
            authors = record.value('authors').split(', ')
            authors = [element.lower() for element in authors]

            adding = True
            list_adding_or = []

            # Loop over the 3 kinds of condition: AND, OR, NOT
            for index, entries in enumerate(author_entries):
                if not entries:
                    continue

                # For each person in the SQL query
                for person in entries.split(','):

                    # Normalize the person's string
                    person = person.lstrip().rstrip().lower()

                    # AND condition
                    if index == 0:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if not matching:
                                adding = False
                                break

                    # OR condition
                    if index == 1:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                list_adding_or.append(True)
                                break
                        else:
                            # Tips for any()
                            # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
                            if any(person in element for element in authors):
                                list_adding_or.append(True)
                            else:
                                list_adding_or.append(False)

                    # NOT condition
                    if index == 2:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                adding = False
                                break

                if True not in list_adding_or and list_adding_or:
                    adding = False
                if not adding:
                    continue

            if adding:
                list_ids.append(record.value('id'))

        if not list_ids:
            requete = "SELECT * FROM papers WHERE id IN ()"
            return requete
        else:
            requete = "SELECT * FROM papers WHERE id IN ("

            # Building the query
            for each_id in list_ids:
                if each_id is not list_ids[-1]:
                    requete = requete + "\"" + str(each_id) + "\"" + ", "
                # Close the query if last
                else:
                    requete = requete + "\"" + str(each_id) + "\"" + ")"

            return requete


    def simpleQuery(self, base):

        """Method to perform a simple search.
        Called from AdvancedSearch, when the user doesn't
        want to save the search"""

        self.query = QtSql.QSqlQuery(self.bdd)

        self.query.prepare(base)
        self.query.exec_()

        self.updateView()

        # Clean graphical abstract area
        try:
            self.scene.clear()
        except AttributeError:
            self.l.warn("Pas d'objet scene pr l'instant.")

        # Cleaning title, authors and abstract
        self.label_author.setText("")
        self.label_title.setText("")
        self.label_date.setText("")
        self.text_abstract.setHtml("")


    def research(self):

        """Slot to search on title and abstract"""

        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
        results = functions.simpleChar(self.research_bar.text())
        proxy.setFilterRegExp(QtCore.QRegExp(results))
        proxy.setFilterKeyColumn(13)
        self.updateCellSize()


    def clearLayout(self, layout):

        """Method to erase the widgets from a layout"""

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                    QtGui.QApplication.processEvents()
                else:
                    self.clearLayout(item.layout())


    def resetView(self):

        """Slot to reset view, clean the graphical abstract, etc"""

        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        # Clean graphical abstract area
        try:
            self.scene.clear()
        except AttributeError:
            self.l.warn("Pas d'objet scene pr l'instant.")

        # Cleaning title, authors and abstract
        self.label_author.setText("")
        self.label_title.setText("")
        self.label_date.setText("")
        self.text_abstract.setHtml("")

        # Uncheck the journals buttons on the left
        for button in self.list_buttons_tags:
            button.setChecked(False)

        self.tags_selected = self.getJournalsToCare()
        self.searchByButton()

        # Reset the proxy fliter
        proxy.setFilterRegExp(QtCore.QRegExp(''))
        proxy.setFilterKeyColumn(2)

        # Clear the search bar
        self.research_bar.clear()

        # Delete last query
        try:
            del self.query
        except AttributeError:
            self.l.warn("Pas de requête précédente")

        self.updateCellSize()


    def markOneRead(self, element):

        """Slot to mark an article read"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
        new = table.model().index(element.row(), 12).data()


        if new == 0:
            return
        else:

            # Save the current line
            line = table.selectionModel().currentIndex().row()

            # Change the data in the model
            table.model().setData(table.model().index(line, 12), 0)

            try:
                model.setQuery(self.query)
                proxy.setSourceModel(model)
                table.setModel(proxy)
            except AttributeError:
                pass

            table.selectRow(line)


    def updateView(self, current_item_id=None):

        """Method to update the view after a model change.
        If an item was selected, the item is re-selected"""

        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        if current_item_id is not None:
            selected_id = current_item_id
        else:
            try:
                selected_id = table.selectionModel().selection().indexes()[0].data()
            except IndexError:
                selected_id = None

        try:
            # Try to update the model
            model.setQuery(self.query)
            proxy.setSourceModel(model)
            table.setModel(proxy)
        except AttributeError:
            model.setQuery(self.refineBaseQuery(table))
            proxy.setSourceModel(model)
            table.setModel(proxy)

        if selected_id is not None:
            for index in range(1, model.rowCount() + 1):
                table.selectRow(index)
                if table.selectionModel().selection().indexes()[0].data() == selected_id:
                    return
            # If we are still here, the old item wasn't found, so deselect all
            table.clearSelection()


    def toggleRead(self):

        """Method to invert the value of new.
        So, toggle the read/unread state of an article"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        # table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        new = table.model().index(table.selectionModel().selection().indexes()[0].row(), 12).data()
        line = table.selectionModel().currentIndex().row()

        # Invert the value of new
        new = 1 - new

        table.model().setData(table.model().index(line, 12), new)

        try:
            model.setQuery(self.query)
            proxy.setSourceModel(model)
            table.setModel(proxy)
        except AttributeError:
            pass

        table.selectRow(line)


    def cleanDb(self):

        """Slot to clean the database. Called from
        the window settings, but better to be here. Also
        deletes the unused pictures present in the graphical_abstracts folder"""

        query = QtSql.QSqlQuery(self.bdd)

        requete = "DELETE FROM papers WHERE journal NOT IN ("

        journals_to_care = self.getJournalsToCare()

        # Building the query
        for each_journal in self.getJournalsToCare():
            if each_journal is not journals_to_care[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            # Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        query.prepare(requete)
        query.exec_()

        self.l.debug("Removed unintersting journals from the database")

        query.exec_("DELETE FROM papers WHERE verif=0")

        self.l.debug("Removed incomplete articles from the database")

        query.exec_("SELECT graphical_abstract FROM papers")

        images_path = []
        while query.next():
            record = query.record()
            images_path.append(record.value('graphical_abstract'))

        images_path = [ path for path in images_path if path != 'Empty' ]

        # Delete all the images which are not in the database (so not
        # corresponding to any article)
        for directory in os.walk("./graphical_abstracts/"):
            for fichier in directory[2]:
                if fichier not in images_path:
                    os.remove(os.path.abspath("./graphical_abstracts/{0}".format(fichier)))

        self.l.debug("Deleted all the useless images")


    def openInBrowser(self):

        """Slot to open the post in browser
        http://stackoverflow.com/questions/4216985/call-to-operating-system-to-open-url
        """

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        url = table.model().index(table.selectionModel().selection().indexes()[0].row(), 10).data()

        if not url:
            return
        else:
            webbrowser.open(url, new=0, autoraise=True)
            self.l.info("Opening {0} in browser".format(url))


    def calculatePercentageMatch(self):

        """Slot to calculate the match percentage"""

        self.predictor = Predictor(self.bdd)
        self.predictor.calculatePercentageMatch()
        self.updateView()


    def toggleLike(self):

        """Slot to mark a post liked"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        like = table.model().index(table.selectionModel().selection().indexes()[0].row(), 9).data()
        line = table.selectionModel().currentIndex().row()

        # Invert the value of new
        if type(like) == int:
            like = 1 - like
        else:
            like = 1

        table.model().setData(table.model().index(line, 9), like)

        try:
            model.setQuery(self.query)
            proxy.setSourceModel(model)
            table.setModel(proxy)
        except AttributeError:
            pass

        table.selectRow(line)


    def initUI(self):

        """Méthode pour créer la fenêtre et régler ses paramètres"""

        # self.setGeometry(0, 25, 1900 , 1020)
        # self.showMaximized()
        self.setWindowTitle('ChemBrows')

        # ------------------------- CONSTRUCTION DES MENUS -------------------------------------------------------------

        self.menubar = self.menuBar()

        # Building files menu
        self.fileMenu = self.menubar.addMenu('&Files')
        self.fileMenu.addAction(self.exitAction)

        # Building edition menu
        self.editMenu = self.menubar.addMenu("&Edition")
        self.editMenu.addAction(self.parseAction)
        self.editMenu.addAction(self.calculatePercentageMatchAction)
        self.editMenu.addAction(self.toggleReadAction)
        self.editMenu.addAction(self.toggleLikeAction)

        self.viewMenu = self.menubar.addMenu("&View")
        self.sortMenu = self.viewMenu.addMenu("Sorting")
        self.sortMenu.addAction(self.sortingPercentageAction)
        self.sortMenu.addAction(self.sortingDateAction)
        self.sortMenu.addAction(self.separatorAction)
        self.sortMenu.addAction(self.sortingReversedAction)

        # Building tools menu
        self.toolMenu = self.menubar.addMenu("&Tools")
        self.toolMenu.addAction(self.openInBrowserAction)

        # Menu entry for the settings
        self.menubar.addAction(self.settingsAction)

        # # ------------------------- TOOLBAR  -----------------------------------------------

        # Create a research bar and set its size
        self.research_bar = QtGui.QLineEdit()
        self.research_bar.setFixedSize(self.research_bar.sizeHint())

        # On ajoute une toolbar en la nommant pr l'indentifier,
        # Puis on ajoute les widgets
        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.addAction(self.parseAction)
        self.toolbar.addAction(self.calculatePercentageMatchAction)
        self.toolbar.addAction(self.toggleLikeAction)
        self.toolbar.addAction(self.updateAction)
        self.toolbar.addAction(self.searchNewAction)

        # Create a button to reset everything
        self.button_back = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_170_step_backward'), 'Back')
        self.toolbar.addWidget(self.button_back)

        self.toolbar.addSeparator()

        self.toolbar.addWidget(QtGui.QLabel('Search : '))
        self.toolbar.addWidget(self.research_bar)
        self.toolbar.addAction(self.searchAction)
        self.toolbar.addAction(self.advanced_searchAction)

        # # Bouton pour afficher la file d'attente
        # self.button_waiting = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_202_shopping_cart'), "File d'attente")
        # self.toolbar.addWidget(self.button_waiting)

        # self.toolbar.addSeparator()

        # # Bouton pour mélanger
        # self.button_shuffle = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_083_random'), "Shuffle")
        # self.toolbar.addWidget(self.button_shuffle)

        # self.toolbar.addSeparator()

        # # Bouton pr afficher les vids non taguées
        # self.button_untag = QtGui.QPushButton("Non tagué")
        # self.toolbar.addWidget(self.button_untag)

        # # ------------------------- LEFT AREA ------------------------------------------------------------------------

        # On crée des scrollarea pr mettre les boutons des tags et des acteurs
        self.scroll_tags = QtGui.QScrollArea()

        # On crée la zone de scrolling
        # http://www.mattmurrayanimation.com/archives/tag/how-do-i-use-a-qscrollarea-in-pyqt
        self.scrolling_tags = QtGui.QWidget()
        self.vbox_all_tags = QtGui.QVBoxLayout()
        self.scrolling_tags.setLayout(self.vbox_all_tags)

        self.scroll_tags.hide()


        # # ------------------------- RIGHT BOTTOM AREA ---------------------------------------------------------------------------

        # The bottom area contains the mosaic (graphical abstract)

        # The bottom are is a simple widget
        self.area_right_bottom = QtGui.QWidget()

        # Personnal graphicsView. Allows the resizing of the mosaic
        self.vision = GraphicsViewPerso(self.area_right_bottom)
        self.vision.setDragMode(GraphicsViewPerso.ScrollHandDrag)

        self.box_mosaic = QtGui.QVBoxLayout()
        self.box_mosaic.addWidget(self.vision)

        self.area_right_bottom.setLayout(self.box_mosaic)

        # ------------------------- RIGHT TOP AREA ------------------------------------------------------------------------------------

        # Creation of a gridLayout to handle the top right area
        self.area_right_top = QtGui.QWidget()
        self.grid_area_right_top = QtGui.QGridLayout()
        self.area_right_top.setLayout(self.grid_area_right_top)

        # Here I set a prelabel: a label w/ just "Title: " to label the title.
        # I set the sizePolicy of this prelabel to the minimum. It will stretch to
        # the minimum. Makes the display better with the grid
        prelabel_title = QtGui.QLabel("Title: ")
        prelabel_title.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_title = QtGui.QLabel()
        self.label_title.setWordWrap(True)
        self.label_title.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        prelabel_author = QtGui.QLabel("Author(s): ")
        prelabel_author.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_author = QtGui.QLabel()
        self.label_author.setWordWrap(True)
        self.label_author.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        prelabel_date = QtGui.QLabel("Published: ")
        prelabel_date.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_date = QtGui.QLabel()
        self.label_date.setWordWrap(True)
        self.label_date.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        # A QWebView to render the sometimes rich text of the abstracts
        self.text_abstract = QtWebKit.QWebView()
        self.web_settings = QtWebKit.QWebSettings.globalSettings()

        # Get the default font and use it for the QWebView
        self.web_settings.setFontFamily(QtWebKit.QWebSettings.StandardFont, self.font().family())
        self.web_settings.setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 18)

        # Building the grid
        self.grid_area_right_top.addWidget(prelabel_title, 0, 0)
        self.grid_area_right_top.addWidget(self.label_title, 0, 1)
        self.grid_area_right_top.addWidget(prelabel_author, 1, 0)
        self.grid_area_right_top.addWidget(self.label_author, 1, 1)
        self.grid_area_right_top.addWidget(prelabel_date, 2, 0)
        self.grid_area_right_top.addWidget(self.label_date, 2, 1)
        self.grid_area_right_top.addWidget(self.text_abstract, 3, 0, 1, 2)

        # # ------------------------- ASSEMBLING THE AREAS ------------------------------------------------------------------------------------

        # Main part of the window in a tab.
        # Allows to create other tabs
        self.onglets = QtGui.QTabWidget()
        self.onglets.setContentsMargins(0, 0, 0, 0)

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter1.addWidget(self.area_right_top)
        self.splitter1.addWidget(self.area_right_bottom)
        # self.vbox_right = QtGui.QVBoxLayout()
        # self.vbox_right.addWidget(self.area_right_top)
        # self.vbox_right.addWidget(self.area_right_bottom)

        self.central_widget = QtGui.QWidget()
        self.hbox_central = QtGui.QHBoxLayout()
        self.central_widget.setLayout(self.hbox_central)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        # self.splitter2.addWidget(self.scroll_tags)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.splitter1)

        self.hbox_central.addWidget(self.scroll_tags)
        self.hbox_central.addWidget(self.splitter2)

        # Create the main table, at index 0
        self.createSearchTab("All articles", "SELECT * FROM papers")

        # self.setCentralWidget(self.splitter2)
        self.setCentralWidget(self.central_widget)

        self.show()


if __name__ == '__main__':

    # Little hack to kill all the pending process
    os.setpgrp()  # create new process group, become its leader
    # app = QtGui.QApplication(sys.argv)
    # ex = Fenetre()
    # sys.exit(app.exec_())
    # os.killpg(0, signal.SIGKILL)  # kill all processes in my group
    try:
        app = QtGui.QApplication(sys.argv)
        ex = Fenetre()
        sys.exit(app.exec_())
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exc_type = type(e).__name__
        fname = exc_tb.tb_frame.f_code.co_filename
        print("File {0}, line {1}".format(fname, exc_tb.tb_lineno))
        print("{0}: {1}".format(exc_type, e))
    finally:
        os.killpg(0, signal.SIGKILL)  # kill all processes in my group
