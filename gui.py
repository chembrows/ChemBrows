#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import signal
import subprocess

from PyQt4 import QtGui, QtSql, QtCore, QtWebKit

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

# sys.path.append('/home/djipey/informatique/python/batbelt')
# import batbelt


class Fenetre(QtGui.QMainWindow):

    def __init__(self):

        super(Fenetre, self).__init__()

        self.l = MyLog()
        self.l.info('Starting the program')

        # Object to store options and preferences
        self.options = QtCore.QSettings("options.ini", QtCore.QSettings.IniFormat)

        # List to store the tags checked
        self.tags_selected = []

        # List to store all the views
        self.liste_tables_in_tabs = []

        self.liste_models_in_tabs = []

        self.liste_proxies_in_tabs = []

        # List to store the tags buttons on the left
        # self.list_buttons_tags = []

        self.connectionBdd()
        self.defineActions()
        self.initUI()
        self.defineSlots()
        self.displayTags()
        self.restoreSettings()


    def connectionBdd(self):

        """Méthode qui se connecte à la bdd, crée un modèle, et l'associe
        à la vue"""

        # Accès à la base de donnée.
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName("fichiers.sqlite")

        self.bdd.open()

        # # Création du modèle, issu de la bdd
        # self.modele = ModelPerso()

        # Changes are effective immediately
        # self.modele.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        # self.modele.setTable("papers")

        query = QtSql.QSqlQuery("fichiers.sqlite")
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                     doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                     liked INTEGER, url TEXT, verif INTEGER, new INTEGER, topic_simple TEXT)")


        # Creation of a custom proxy to fix a sorting bug and to filter
        # articles while researching
        # self.proxy = ProxyPerso(self)
        # self.proxy.setSourceModel(self.modele)

        # # To fix a sorting bug
        # self.proxy.setDynamicSortFilter(True)

        # Create the view, and give it the model
        # self.tableau = ViewPerso(self)
        # self.tableau.setModel(self.proxy)
        # self.tableau.setItemDelegate(ViewDelegate(self))
        # self.tableau.setSelectionBehavior(self.tableau.SelectRows)


    def getJournalsToCare(self):

        """Get the journals checked in the settings window"""

        # Create a list to store the journals checked in the settings window
        self.journals_to_care = self.options.value("journals_to_parse", [])

        # If no journals to care in the settings,
        # take them all. So build a journals_to_care list
        # with all the journals
        if not self.journals_to_care:
            # self.journals_to_care = []
            for company in os.listdir("./journals"):
                with open('journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        # Take the abbreviation
                        self.journals_to_care.append(line.split(" : ")[1])


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

        for site in urls:
            # One worker for each website
            worker = Worker(site, self.l)
            worker.finished.connect(self.checkThreads)
            self.list_threads.append(worker)

        self.resetView()


    def checkThreads(self):

        """Method to check the state of each worker.
        If all the workers are finished, enable the parse action"""

        model = self.liste_models_in_tabs[self.onglets.currentIndex()]

        # Get a list of the workers states
        list_states = [worker.isFinished() for worker in self.list_threads]

        if False not in list_states:
            # Update the view when a worker is finished
            model.select()
            self.parseAction.setEnabled(True)
            self.l.debug("Parsing data finished. Enabling parseAction")


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
        self.settingsAction = QtGui.QAction('Settings', self)
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


        # # On crée une action qui servira de séparateur
        # self.separatorAction = QtGui.QAction(self)
        # self.separatorAction.setSeparator(True)

        # # On crée une action pour les réglages, et on lui passe en
        # # paramètres la fenêtre principale, et l'objet pr la sauvegarde
        # self.settingsAction = QtGui.QAction('Préférences', self)
        # self.settingsAction.triggered.connect(lambda: Settings(self))

        # # Action pr changer d'onglet
        # self.changeTabRightAction = QtGui.QAction("Changer d'onglet", self)
        # self.changeTabRightAction.setShortcut('C')
        # self.changeTabRightAction.triggered.connect(self.changeTabRight)
        # # On ajoute l'action à la fenêtre seulement pr la rendre invisible
        # # http://stackoverflow.com/questions/18441755/hide-an-action-without-disabling-it
        # self.addAction(self.changeTabRightAction)


    def updateModel(self):

        """Debug function, allows to update a model
        with a button, at any time. Will not be used by
        the final user"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        model.select()

        model.setQuery(self.query)
        proxy.setSourceModel(model)
        table.setModel(proxy)


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

        self.options.setValue("central_splitter", self.splitter1.saveState())
        self.options.setValue("final_splitter", self.splitter2.saveState())

        self.options.endGroup()

        # Save the checked journals (on the left)
        tags_checked = [button.text() for button in self.list_buttons_tags if button.isChecked()]

        self.options.setValue("tags_checked", tags_checked)

        # On s'assure que self.options finit ttes ces taches.
        # Corrige un bug. self.options semble ne pas effectuer
        # ttes ces tâches immédiatement.
        self.options.sync()

        self.bdd.removeDatabase("fichiers.sqlite")
        self.bdd.close()

        QtGui.qApp.quit()

        self.l.info("Fermeture du programme")


    def restoreSettings(self):

        """Restore the prefs"""

        searches_saved = QtCore.QSettings("searches.ini", QtCore.QSettings.IniFormat)

        # Restore the saved searches
        for query in searches_saved.childGroups():
            search_name = query
            query = searches_saved.value("{0}/sql_query".format(query))
            self.createSearchTab(search_name, query)

        # Si des réglages pour la fenêtre
        # sont disponibles, on les importe et applique
        if "Window" in self.options.childGroups():
            self.restoreGeometry(self.options.value("Window/window_geometry"))
            self.restoreState(self.options.value("Window/window_state"))

            for index, each_table in enumerate(self.liste_tables_in_tabs):
                each_table.horizontalHeader().restoreState(self.options.value("Window/header_state{0}".format(index)))

            self.splitter1.restoreState(self.options.value("Window/central_splitter"))
            self.splitter2.restoreState(self.options.value("Window/final_splitter"))



        self.getJournalsToCare()

        self.tags_selected = self.journals_to_care
        self.searchByButton()


    def popup(self, pos):

        """Method to handle right-click"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        if not table.selectionModel().selection().indexes():
            return
        else:
        # Si une ligne est sélectionnée, on affiche un menu adapté à une
        # seule sélection
        # elif len(self.tableau.selectionModel().selection().indexes()) == 11:
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

        # On connecte le signal de double clic sur une cell vers un
        # slot qui lance le lecteur ac le nom du fichier en paramètre
        # self.tableau.doubleClicked.connect(self.openInBrowser)

        # # http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        # # Personal right-click
        # self.tableau.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.tableau.customContextMenuRequested.connect(self.popup)

        # self.tableau.clicked.connect(self.displayInfos)
        # self.tableau.clicked.connect(self.displayMosaic)
        # self.tableau.clicked.connect(self.markOneRead)

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

        new_size = self.splitter2.sizes()[1]

        for table in self.liste_tables_in_tabs:
            table.resizeCells(new_size)


    def keyPressEvent(self, e):

        """On réimplémente la gestion des évènements
        dans cette méthode"""

        # # TODO: trouver un moyen de re-sélectionner la cell
        # # après édition

        # key = e.key()

        # # Si l'event clavier est un appui sur F2
        # if key == QtCore.Qt.Key_F2 and self.tableau.hasFocus():
            # # On utilise un try pour le cas où aucune cell n'est sélectionnée
            # try:
                # # On édite la cell de nom de la ligne sélectionnée
                # # http://stackoverflow.com/questions/8157688/
                # # specifying-an-index-in-qtableview-with-pyqt
                # self.tableau.edit(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 1))
            # except IndexError:
                # self.l.warn("Pas de cell sélectionnée")

        # # Si on presse la touche entrée, on lance le fichier sélectionné
        # elif key == QtCore.Qt.Key_Return and self.tableau.hasFocus():
            # try:
                # # TODO: si le fichier n'est pas accessible, ne pas lancer
                # self.launchFile()
            # except IndexError:
                # self.l.warn("Aucun fichier sélectionné")

        # for plugin in self.plugins:
            # self.plugins[plugin].keyPressed(e)
        e.ignore()

        pass


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

        # On obtient le path de la mosaique grâce au path de la thumb
        path_graphical_abstract = "./graphical_abstracts/" + path_graphical_abstract

        w_vue, h_vue = self.vision.width(), self.vision.height()
        self.current_image = QtGui.QImage(path_graphical_abstract)

        self.pixmap = QtGui.QPixmap.fromImage(self.current_image.scaled(w_vue, h_vue,
                                              QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        w_pix, h_pix = self.pixmap.width(), self.pixmap.height()

        self.scene = QtGui.QGraphicsScene()

        # On recentre un peu l'image
        self.scene.setSceneRect(0, 0, w_pix, h_pix - 10)
        self.scene.addPixmap(self.pixmap)
        self.vision.setScene(self.scene)


    def tabChanged(self):

        """Slot to perform some actions when the current tab is changed.
        Mainly sets the tab query to the saved query"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery("fichiers.sqlite")

        self.query.prepare(table.base_query)

        self.query.exec_()

        model.setQuery(self.query)

        model.setQuery(self.query)
        proxy.setSourceModel(model)
        table.setModel(proxy)

        # Update the size of the columns of the view if the central
        # splitter moved
        self.updateCellSize()


    def createSearchTab(self, name_search, query, update=False):

        """Slot called from AdvancedSearch, when a new search is added,
        or a previous one updated"""

        # If the tab's query is updated from the advancedSearch window,
        # just update the base_query
        if update:
            for index in range(self.onglets.count()):
                if name_search == self.onglets.tabText(index):
                    self.liste_tables_in_tabs[index].base_query = query
                    # TODO: update the view
                    return

        # Create the model for the new tab
        modele = ModelPerso()

        # Changes are effective immediately
        modele.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        modele.setTable("papers")

        self.liste_models_in_tabs.append(modele)

        # proxy = ProxyPerso(self)
        proxy = QtGui.QSortFilterProxyModel()
        proxy.setDynamicSortFilter(True)
        proxy.setSourceModel(modele)
        self.liste_proxies_in_tabs.append(proxy)

        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.base_query = query
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

        self.getJournalsToCare()

        self.journals_to_care.sort()

        for journal in self.journals_to_care:

            button = QtGui.QPushButton(journal)
            button.setCheckable(True)
            button.adjustSize()

            button.clicked[bool].connect(self.stateButtons)
            self.vbox_all_tags.addWidget(button)

            self.list_buttons_tags.append(button)

        self.vbox_all_tags.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_tags.setWidget(self.scrolling_tags)

        # TODO: j'en suis ici, query de base
        # self.searchByButton()


    def stateButtons(self, pressed):

        """Slot to check the journals push buttons"""

        self.getJournalsToCare()

        if self.tags_selected == self.journals_to_care:
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
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery("fichiers.sqlite")

        # requete = "SELECT * FROM papers WHERE journal IN ("

        # TODO: ajouter à la base_query
        if "WHERE" in table.base_query:
            requete = " AND journal IN ("
        else:
            requete = " WHERE journal IN ("

        # Building the query
        for each_journal in self.tags_selected:
            if each_journal is not self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            # Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(table.base_query + requete)
        self.query.exec_()

        # Update the view
        model.setQuery(self.query)
        proxy.setSourceModel(model)
        table.setModel(proxy)


    def searchNew(self):

        """Slot to select new articles"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery("fichiers.sqlite")

        # First, search the new articles id
        self.query.prepare("SELECT id FROM papers WHERE new=1")
        self.query.exec_()

        list_id = []
        while self.query.next():
            record = self.query.record()
            list_id.append(record.value('id'))

        # Then, perform the query on the id. This way, the articles
        # are not erased from the view when they are marked as read
        requete = "SELECT * FROM papers WHERE id IN ("

        # Building the query
        for each_id in list_id:
            if each_id is not list_id[-1]:
                requete = requete + str(each_id) + ", "
            # Close the query if last
            else:
                requete = requete + str(each_id) + ")"

        self.query.prepare(requete)
        self.query.exec_()

        model.setQuery(self.query)
        proxy.setSourceModel(model)
        table.setModel(proxy)


    def simpleQuery(self, base):

        """Method to perform a simple search.
        Called from AdvancedSearch, when the user doesn't
        want to save the search"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        self.query = QtSql.QSqlQuery("fichiers.sqlite")

        self.query.prepare(base)
        self.query.exec_()

        # Update the view
        model.setQuery(self.query)
        proxy.setSourceModel(model)
        table.setModel(proxy)


    def research(self):

        """Slot to search on title and abstract"""

        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
        results = functions.simpleChar(self.research_bar.text())
        proxy.setFilterRegExp(QtCore.QRegExp(results))
        proxy.setFilterKeyColumn(13)

        # table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        # model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        # proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]

        # # results = functions.simpleChar(self.research_bar.text())
        # results = functions.queryString(self.research_bar.text())

        # self.query = QtSql.QSqlQuery("fichiers.sqlite")

        # base = "SELECT * FROM papers WHERE ' ' || replace(authors, ',', ' ') || ' ' \
                # LIKE '{0}' OR topic_simple LIKE '{0}'".format(results)

        # self.query.prepare(base)
        # self.query.exec_()

        # print(self.query.lastQuery())

        # model.setQuery(self.query)
        # proxy.setSourceModel(model)
        # table.setModel(proxy)

    # def adjustView(self):

        # """Adjust the view, eg: hide the unintersting columns"""

        # self.tableau.hideColumn(0)  # Hide id
        # self.tableau.hideColumn(2)  # Hide doi
        # self.tableau.hideColumn(6)  # Hide authors
        # self.tableau.hideColumn(7)  # Hide abstracts
        # self.tableau.hideColumn(8)  # Hide abstracts
        # self.tableau.hideColumn(10)  # Hide urls
        # self.tableau.hideColumn(11)  # Hide verif
        # self.tableau.hideColumn(12)  # Hide new


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

        """Slot pour remettre les données affichées à zéro"""

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

        self.tags_selected = self.journals_to_care
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


    def markOneRead(self, element):

        """Slot to mark an article read"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
        new = table.model().index(element.row(), 12).data()

        if new == 0:
            return
        else:

            line = table.selectionModel().currentIndex().row()

            table.model().setData(table.model().index(line, 12), 0)

            try:
                model.setQuery(self.query)
                proxy.setSourceModel(model)
                table.setModel(proxy)
            except AttributeError:
                pass

            table.selectRow(line)


    def toggleRead(self):

        """Method to invert the value of new.
        So, toggle the read/unread state of an article"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]
        model = self.liste_models_in_tabs[self.onglets.currentIndex()]
        proxy = self.liste_proxies_in_tabs[self.onglets.currentIndex()]
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

        query = QtSql.QSqlQuery("fichiers.sqlite")

        requete = "DELETE FROM papers WHERE journal NOT IN ("

        # Building the query
        for each_journal in self.journals_to_care:
            if each_journal is not self.journals_to_care[-1]:
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

        """Slot to open the post in browser"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        url = table.model().index(table.selectionModel().selection().indexes()[0].row(), 10).data()

        if not url:
            return

        cmd = subprocess.Popen(['firefox', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = cmd.communicate()

        if cmd.returncode != 0:
            self.l.warn("Problem while opening post in browser")
        else:
            self.l.info("Opening {0} in browser".format(url))


    def calculatePercentageMatch(self):

        """Slot to calculate the match percentage"""

        model = self.liste_models_in_tabs[self.onglets.currentIndex()]

        self.predictor = Predictor(self.bdd)
        self.predictor.calculatePercentageMatch()
        model.select()


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
            self.proxy.setSourceModel(model)
            table.setModel(proxy)
        except AttributeError:
            pass

        table.selectRow(line)


    def postsSelected(self, previous=False):

        """Method to get the selected posts, and store the current
        selected line before updating the model"""

        table = self.liste_tables_in_tabs[self.onglets.currentIndex()]

        posts_selected = []
        lignes = []

        # On récupère ttes les cells sélectionnées
        for element in table.selectionModel().selection().indexes():
            lignes.append(element.row())
            # element est un QModelIndex. Comme on sélectionne des lignes
            # entières, on a ttes les colonnes de ttes les lignes ds
            # cette boucle. Si on n'est pas sur la colonne de l'id, on break
            # car inutile.
            if element.column() == 0:
                # On récupère l'id de la vid sélectionnée
                new_id = element.data()
            else:
                continue

            # Si l'id d'une vid sélectionnée n'est pas ds déjà ds la liste,
            # on l'y ajoute
            if not new_id in posts_selected:
                posts_selected.append(new_id)

        if previous:
            # On récupère les LIGNES de la vue correspondant
            # aux vids sélectionnées
            lignes = list(set(lignes))
            return posts_selected, lignes
        else:
            return posts_selected


    def initUI(self):

        """Méthode pour créer la fenêtre et régler ses paramètres"""

        # self.setGeometry(0, 25, 1900 , 1020)
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

        # Building tools menu
        self.toolMenu = self.menubar.addMenu("&Tools")
        self.toolMenu.addAction(self.openInBrowserAction)

        self.menubar.addAction(self.settingsAction)

        # # Ajout d'une entrée pr les réglages dans la barre
        # # des menus
        # self.menubar.addAction(self.settingsAction)

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

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter1.addWidget(self.area_right_top)
        self.splitter1.addWidget(self.area_right_bottom)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter2.addWidget(self.scroll_tags)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.splitter1)

        # Create the main table, at index 0
        self.createSearchTab("All articles", "SELECT * FROM papers")


        self.setCentralWidget(self.splitter2)

        self.show()


if __name__ == '__main__':

    # Little hack to kill all the pending process
    os.setpgrp()  # create new process group, become its leader
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
