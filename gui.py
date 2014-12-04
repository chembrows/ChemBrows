#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import signal
import numpy as np
import feedparser
import subprocess

from PyQt4 import QtGui, QtSql, QtCore, QtWebKit

#Personal modules
from log import MyLog
from model import ModelPerso
from view import ViewPerso
from graphicsview import GraphicsViewPerso
from view_delegate import ViewDelegate
from worker import Worker
from predictor import Predictor
from settings import Settings
import functions


sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt


class Fenetre(QtGui.QMainWindow):
    

    def __init__(self):

        super(Fenetre, self).__init__()
        self.l = MyLog()
        self.l.info('Starting the program')

        #Object to store options and preferences
        self.options = QtCore.QSettings("options.ini", QtCore.QSettings.IniFormat)

        #List to store the tags checked
        self.tags_selected = []

        #List to store the tags buttons on the left
        #self.list_buttons_tags = []

        self.connectionBdd()
        self.defineActions()
        self.initUI()
        self.defineSlots()
        self.displayTags()
        self.restoreSettings()


    def connectionBdd(self):

        """Méthode qui se connecte à la bdd, crée un modèle, et l'associe
        à la vue"""

        #Accès à la base de donnée.
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName("fichiers.sqlite")
        self.bdd.open()


        #Création du modèle, issu de la bdd
        self.modele = ModelPerso()

        #Changes are effective immediately
        self.modele.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.modele.setTable("papers")

        query = QtSql.QSqlQuery("fichiers.sqlite")
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                     doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                     liked INTEGER, url TEXT, verif INTEGER, new INTEGER)")


        #self.modele.select() # Remplit le modèle avec les data de la table

        #On crée un proxy pour filtrer les fichiers lors
        #des recherches
        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.modele)

        #Règle le bug du tri après une modif de la bdd
        self.proxy.setDynamicSortFilter(True)

        #On crée la vue (un tableau), et on lui associe le modèle créé
        #précédemment
        self.tableau = ViewPerso(self)
        self.tableau.setModel(self.proxy)
        self.tableau.setItemDelegate(ViewDelegate(self))
        self.tableau.setSelectionBehavior(self.tableau.SelectRows)


        #self.adjustView()


    def getJournalsToCare(self):

        #Create a list to store the journals checked in the settings window
        self.journals_to_care = self.options.value("journals_to_parse", [])

        #If no journals to care in the settings,
        #take them all. So build a journals_to_care list
        #with all the journals
        if not self.journals_to_care:
            #self.journals_to_care = []
            for company in os.listdir("./journals"):
                with open('journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        #Take the abbreviation
                        self.journals_to_care.append(line.split(" : ")[1])


    def parse(self):

        """Method to start the parsing of the data"""

        journals_to_parse = self.options.value("journals_to_parse", [])

        #If no journals to parse in the settings,
        #parse them all. So build a journals_to_parse list
        #with all the journals
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

        #Disabling the parse action to avoid double start
        self.parseAction.setEnabled(False)

        #List to store the threads.
        #The list is cleared when the method is started
        self.list_threads = []

        for site in urls:
            #One worker for each website
            worker = Worker(site, self.l)
            worker.finished.connect(self.checkThreads)
            self.list_threads.append(worker)

        self.resetView()


    def checkThreads(self):

        """Method to check the state of each worker.
        If all the workers are finished, enable the parse action"""

        #Get a list of the workers states
        list_states = [ worker.isFinished() for worker in self.list_threads ]

        if not False in list_states:
            #Update the view when a worker is finished
            self.modele.select()
            self.parseAction.setEnabled(True)
            self.l.debug("Parsing data finished. Enabling parseAction")


    def defineActions(self):

        """On définit ici les actions du programme. Cette méthode est
        appelée à la création de la classe"""

        #Action to quit
        self.exitAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_063_power'), '&Quitter', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Quit")
        self.exitAction.triggered.connect(self.closeEvent)

        #Action to refresh the posts
        self.parseAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_081_refresh.png'), '&Refresh', self)        
        self.parseAction.setShortcut('F5')
        self.parseAction.setStatusTip("Download new posts")
        self.parseAction.triggered.connect(self.parse)

        #Action to calculate the percentages of match
        self.calculatePercentageMatchAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_040_stats.png'), '&Percentages', self)        
        self.calculatePercentageMatchAction.setShortcut('F6')
        self.calculatePercentageMatchAction.setStatusTip("Calculate percentages")
        self.calculatePercentageMatchAction.triggered.connect(self.calculatePercentageMatch)

        #Action to like a post
        self.likeAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_343_thumbs_up'), 'Like the post', self)
        self.likeAction.setShortcut('L')
        self.likeAction.triggered.connect(self.like)

        #Action to unlike a post
        self.unLikeAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_344_thumbs_down'), 'unLike the post', self)
        self.unLikeAction.setShortcut('U')
        self.unLikeAction.triggered.connect(self.unLike)

        #Action to open the post in browser
        self.openInBrowserAction = QtGui.QAction('Open post in browser', self)
        self.openInBrowserAction.triggered.connect(self.openInBrowser)
        self.openInBrowserAction.setShortcut('Ctrl+W')

        #Action to update the model. For TEST
        self.updateAction = QtGui.QAction('Update model', self)
        self.updateAction.triggered.connect(lambda: self.modele.select())
        self.updateAction.setShortcut('F7')

        #Action to show a settings window
        self.settingsAction = QtGui.QAction('Settings', self)
        self.settingsAction.triggered.connect(lambda: Settings(self))

        #Action so show new articles
        self.searchNewAction = QtGui.QAction('Search new', self)
        self.searchNewAction.triggered.connect(self.searchNew)

        ##Action pour enlever un tag
        #self.removeTagAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_207_remove_2.png'), 'Supprimer un tag', self)
        #self.removeTagAction.setShortcut('R')
        #self.removeTagAction.setStatusTip("Enlever un tag à une vidéo")
        #self.removeTagAction.triggered.connect(self.removeTag)

        ##Action pour la vérif des pathes en bdd
        #self.verificationAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_081_refresh.png'), 'Vérification bdd', self)
        #self.verificationAction.setShortcut('F5')
        #self.verificationAction.triggered.connect(self.verification)

        ##Action pr ajouter un tag
        #self.addTagAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_065_tag.png'), '&Ajouter un tag', self)
        #self.addTagAction.setShortcut('T')
        #self.addTagAction.triggered.connect(self.addTag)

        ##On crée une action qui servira de séparateur
        #self.separatorAction = QtGui.QAction(self)
        #self.separatorAction.setSeparator(True)

        ##On crée une action pour les réglages, et on lui passe en 
        ##paramètres la fenêtre principale, et l'objet pr la sauvegarde
        #self.settingsAction = QtGui.QAction('Préférences', self)
        #self.settingsAction.triggered.connect(lambda: Settings(self))

        ##Action pr changer d'onglet
        #self.changeTabRightAction = QtGui.QAction("Changer d'onglet", self)
        #self.changeTabRightAction.setShortcut('C')
        #self.changeTabRightAction.triggered.connect(self.changeTabRight)
        ##On ajoute l'action à la fenêtre seulement pr la rendre invisible
        ##http://stackoverflow.com/questions/18441755/hide-an-action-without-disabling-it
        #self.addAction(self.changeTabRightAction)


    def closeEvent(self, event):

        """Méthode pr effetcuer des actions avant de
        quitter, comme sauver les options dans un fichier 
        de conf"""

        ##http://stackoverflow.com/questions/9249500/
        ##pyside-pyqt-detect-if-user-trying-to-close-window

        #Record the window state and appearance
        self.options.beginGroup("Window")

        #Reinitializing the keys
        self.options.remove("")

        self.l.debug("Sauvegarde de l'état de la fenêtre dans options.ini")
        self.options.setValue("window_geometry", self.saveGeometry())
        self.options.setValue("window_state", self.saveState())
        self.options.setValue("header_state", self.tableau.horizontalHeader().saveState())
        self.options.setValue("central_splitter", self.splitter1.saveState())
        self.options.setValue("final_splitter", self.splitter2.saveState())

        self.options.endGroup()

        #Save the checked journals (on the left)
        #tags_checked = [ button.text() for button in self.list_buttons_tags if button.isChecked() ]

        #self.options.setValue("tags_checked", tags_checked)

        #On s'assure que self.options finit ttes ces taches.
        #Corrige un bug. self.options semble ne pas effectuer
        #ttes ces tâches immédiatement.
        self.options.sync()

        self.bdd.removeDatabase("fichiers.sqlite")
        self.bdd.close()

        QtGui.qApp.quit()

        self.l.info("Fermeture du programme")


    def restoreSettings(self):

        """Restore the prefs"""

        #Si des réglages pour la fenêtre
        #sont disponibles, on les importe et applique
        if "Window" in self.options.childGroups():
            self.restoreGeometry(self.options.value("Window/window_geometry"))
            self.restoreState(self.options.value("Window/window_state"))
            self.tableau.horizontalHeader().restoreState(self.options.value("Window/header_state"))
            self.splitter1.restoreState(self.options.value("Window/central_splitter"))
            self.splitter2.restoreState(self.options.value("Window/final_splitter"))


        self.getJournalsToCare()

        self.tags_selected = self.journals_to_care
        self.searchByButton()


    def popup(self, pos):

        """Method to handle right-click"""

        if not self.tableau.selectionModel().selection().indexes():
            return
        else:
        #Si une ligne est sélectionnée, on affiche un menu adapté à une
        #seule sélection
        #elif len(self.tableau.selectionModel().selection().indexes()) == 11:
            self.displayInfos()
            self.displayMosaic()

        #Define a new postition for the menu
        new_pos = QtCore.QPoint(pos.x()+ 240, pos.y() + 120)

        #Create the right-click menu and add the actions
        menu = QtGui.QMenu()
        menu.addAction(self.likeAction)
        menu.addAction(self.unLikeAction)
        menu.addAction(self.openInBrowserAction)
        action = menu.exec_(self.mapToGlobal(new_pos))


    def defineSlots(self):

        """Connect the slots"""

        #On connecte le signal de double clic sur une cell vers un
        #slot qui lance le lecteur ac le nom du fichier en paramètre
        self.tableau.doubleClicked.connect(self.openInBrowser)

        #http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        #Le clic droit est perso
        self.tableau.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableau.customContextMenuRequested.connect(self.popup)

        self.tableau.clicked.connect(self.displayInfos)
        self.tableau.clicked.connect(self.displayMosaic)
        self.tableau.clicked.connect(self.markOneRead)

        #Connect the back button
        self.button_back.clicked.connect(self.resetView)


    def keyPressEvent(self, e):

        """On réimplémente la gestion des évènements
        dans cette méthode"""

        ##TODO: trouver un moyen de re-sélectionner la cell
        ##après édition

        #key = e.key()

        ##Si l'event clavier est un appui sur F2
        #if key == QtCore.Qt.Key_F2 and self.tableau.hasFocus():
            ##On utilise un try pour le cas où aucune cell n'est sélectionnée
            #try:
                ##On édite la cell de nom de la ligne sélectionnée
                ##http://stackoverflow.com/questions/8157688/
                ##specifying-an-index-in-qtableview-with-pyqt
                #self.tableau.edit(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 1))
            #except IndexError:
                #self.l.warn("Pas de cell sélectionnée")

        ##Si on presse la touche entrée, on lance le fichier sélectionné
        #elif key == QtCore.Qt.Key_Return and self.tableau.hasFocus():
            #try:
                ##TODO: si le fichier n'est pas accessible, ne pas lancer
                #self.launchFile()
            #except IndexError:
                #self.l.warn("Aucun fichier sélectionné")

        #for plugin in self.plugins:
            #self.plugins[plugin].keyPressed(e)
        e.ignore()

        pass


    def displayInfos(self):

        """Method to get the infos of a post.
        For now, gets only the abstract"""

        try:
            #self.text_abstract.setText(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 7).data())
            self.text_abstract.setHtml(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 7).data())
            title = self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 3).data()
            author = self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 6).data()
        except TypeError:
            self.l.debug("No abstract for this post, displayInfos()")
            self.text_abstract.setHtml("")

        self.label_title.setText("<span style='font-size:12pt; font-weight:bold'>{0}</span>".format(title))
        self.label_author.setText(author)


    def displayMosaic(self):

        """Slot qui affiche la mosaïque de la vidéo dans
        la partie droite"""
        #infos:
        #http://vincent-vande-vyvre.developpez.com/tutoriels/pyqt/manipulation-images/

        try:
            path_graphical_abstract = self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 8).data()
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

        #On obtient le path de la mosaique grâce au path de la thumb
        path_graphical_abstract = "./graphical_abstracts/" + path_graphical_abstract

        w_vue, h_vue = self.vision.width(), self.vision.height() 
        self.current_image = QtGui.QImage(path_graphical_abstract)

        self.pixmap = QtGui.QPixmap.fromImage(self.current_image.scaled(w_vue, h_vue,
                                                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)) 

        w_pix, h_pix = self.pixmap.width(), self.pixmap.height()

        self.scene = QtGui.QGraphicsScene()

        #On recentre un peu l'image
        self.scene.setSceneRect(0, 0, w_pix , h_pix - 10)
        self.scene.addPixmap(self.pixmap)
        self.vision.setScene(self.scene)


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
        self.searchByButton()


    def stateButtons(self, pressed):

        """Slot to check the journals push buttons"""

        self.getJournalsToCare()

        if self.tags_selected == self.journals_to_care:
            self.tags_selected = []

        #Get the button pressed
        source = self.sender()

        #Build the list of ON buttons
        if source.parent() == self.scrolling_tags:
            if pressed:
                self.tags_selected.append(source.text())
            else:
                self.tags_selected.remove(source.text())

        self.searchByButton()


    def searchByButton(self):

        """Slot to select articles by journal"""

        #Reset the view when the last button is unchecked
        if not self.tags_selected:
            self.resetView()
            return

        self.query = QtSql.QSqlQuery()

        requete = "SELECT * FROM papers WHERE journal IN ("

        #Building the query
        for each_journal in self.tags_selected:
            if each_journal is not self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            #Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(requete)
        self.query.exec_()

        #Update the view
        #self.modele.setTable("papers")
        self.modele.setQuery(self.query)

        self.proxy.setSourceModel(self.modele)
        self.tableau.setModel(self.proxy)
        #self.adjustView()


    def searchNew(self):

        """Slot to select new articles"""

        self.query = QtSql.QSqlQuery()

        #First, search the new articles id
        self.query.prepare("SELECT id FROM papers WHERE new=1")
        self.query.exec_()

        list_id = []
        while self.query.next():
            record = self.query.record()
            list_id.append(record.value('id'))


        #Then, perform the query on the id. This way, the articles
        #are not erased from the view when they are marked as read
        requete = "SELECT * FROM papers WHERE id IN ("

        #Building the query
        for each_id in list_id:
            if each_id is not list_id[-1]:
                requete = requete + str(each_id) + ", "
            #Close the query if last
            else:
                requete = requete + str(each_id) + ")"

        self.query.prepare(requete)
        self.query.exec_()

        #Update the view
        #self.modele.setTable("papers")
        self.modele.setQuery(self.query)

        self.proxy.setSourceModel(self.modele)
        self.tableau.setModel(self.proxy)
        #self.adjustView()


    def adjustView(self):

        """Adjust the view, eg: hide the unintersting columns"""

        self.tableau.hideColumn(0) #Hide id
        self.tableau.hideColumn(2) #Hide doi
        self.tableau.hideColumn(6) #Hide authors
        self.tableau.hideColumn(7) #Hide abstracts
        self.tableau.hideColumn(8) #Hide abstracts
        self.tableau.hideColumn(10) #Hide urls
        self.tableau.hideColumn(11) #Hide verif
        self.tableau.hideColumn(12) #Hide new


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

        #Clean graphical abstract area
        try:
            self.scene.clear()
        except AttributeError:
            self.l.warn("Pas d'objet scene pr l'instant.")

        #Cleaning title, authors and abstract
        self.label_author.setText("")
        self.label_title.setText("")
        self.text_abstract.setHtml("")

        #Uncheck the journals buttons on the left
        for button in self.list_buttons_tags:
            button.setChecked(False)

        #Save header
        try:
            self.header_state
        except AttributeError:
            self.header_state = self.tableau.horizontalHeader().saveState() 


        self.tags_selected = self.journals_to_care
        self.searchByButton()

        #self.proxy.setFilterRegExp(QtCore.QRegExp(''))
        #self.proxy.setFilterKeyColumn(2)

        #On efface la barre de recherche
        #self.research_bar.clear()

        #Delete last query
        try:
            del self.query
        except AttributeError:
            self.l.warn("Pas de requête précédente")

        #self.adjustView()


    def launchFile(self):

        """Slot qui lance le fichier double cliqué dans le tableau
        On accède à l'index en rajoutant un argument à la def du slot,
        même si on ne le spécifie pas ds l'appel"""

        ##TODO: pouvoir choisir le player grâce à un fichier de conf
        #path = self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 4).data()
        #path_player = self.options.value("player", "/usr/bin/vlc")

        #self.l.info("{0} lancé".format(path))
        #os.popen("{0} \"{1}\"".format(path_player, path))

        pass


    def markOneRead(self, element):

        """Slot to mark an article read"""

        new = self.tableau.model().index(element.row(), 12).data()

        if new == 0:
            return
        else:

            id_bdd = self.tableau.model().index(element.row(), 0).data()

            line = self.tableau.selectionModel().currentIndex().row()

            query = QtSql.QSqlQuery("fichiers.sqlite")

            query.prepare("UPDATE papers SET new = ? WHERE id = ?")
            params = (0, id_bdd)

            for value in params:
                query.addBindValue(value)

            query.exec_()

            self.modele.select()

            try:
                self.modele.setQuery(self.query)
                self.proxy.setSourceModel(self.modele)
                self.tableau.setModel(self.proxy)
                #self.adjustView()
            except AttributeError:
                pass

            self.tableau.selectRow(line)


    def cleanDb(self):

        """Slot to clean the database. Called from
        the window settings, but better to be here"""

        self.query = QtSql.QSqlQuery()

        #requete = "SELECT * FROM papers WHERE journal IN ("
        requete = "DELETE FROM papers WHERE journal NOT IN ("

        #Building the query
        for each_journal in self.journals_to_care:
            if each_journal is not self.journals_to_care[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            #Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(requete)
        self.query.exec_()

        self.query.exec_("DELETE FROM papers WHERE verif=0")

        self.l.debug("Removing unintersting journals from the database")


    def openInBrowser(self):

        """Slot to open the post in browser"""

        url = self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 10).data()

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

        self.predictor = Predictor(self.bdd)
        self.predictor.calculatePercentageMatch()
        self.modele.select()


    def like(self):

        """Slot to mark a post like"""

        posts_selected, previous_lines = self.postsSelected(True)

        if not posts_selected:
            return

        functions.like(posts_selected[0], self.l)

        #try:
        ##On régènére la vue courante en effectuant la même
        ##requête que précédemment
            #self.query.prepare(self.query.executedQuery())
            #self.query.exec_()
            #self.modele.setTable("videos")
            #self.modele.setQuery(self.query)
        #except AttributeError:
            #self.l.warn("Pas de requête précédente")
            #self.modele.setTable("videos")
            #self.modele.select()

        self.modele.select()

        try:
            self.modele.setQuery(self.query)
            self.proxy.setSourceModel(self.modele)
            self.tableau.setModel(self.proxy)
            #self.adjustView()
        except AttributeError:
            pass

        self.tableau.selectRow(previous_lines[0])


    def unLike(self):

        """Slot to mark a post unlike"""

        posts_selected, previous_lines = self.postsSelected(True)

        if not posts_selected:
            return

        functions.unLike(posts_selected[0], self.l)

        self.modele.select()
        self.proxy.setSourceModel(self.modele)
        self.tableau.setModel(self.proxy)

        self.tableau.selectRow(previous_lines[0])


    def postsSelected(self, previous=False):

        """Method to get the selected posts, and store the current
        selected line before updating the model"""

        posts_selected = []
        lignes = []

        #On récupère ttes les cells sélectionnées
        for element in self.tableau.selectionModel().selection().indexes():
            lignes.append(element.row())
            #element est un QModelIndex. Comme on sélectionne des lignes
            #entières, on a ttes les colonnes de ttes les lignes ds
            #cette boucle. Si on n'est pas sur la colonne de l'id, on break
            #car inutile.
            if element.column() == 0:
                #On récupère l'id de la vid sélectionnée
                new_id = element.data()
            else:
                continue

            #Si l'id d'une vid sélectionnée n'est pas ds déjà ds la liste,
            #on l'y ajoute
            if not new_id in posts_selected:
                posts_selected.append(new_id)

        if previous:
            #On récupère les LIGNES de la vue correspondant
            #aux vids sélectionnées
            lignes = list(set(lignes))
            return posts_selected, lignes
        else:
            return posts_selected


    def initUI(self):               

        """Méthode pour créer la fenêtre et régler ses paramètres"""

        #self.setGeometry(0, 25, 1900 , 1020)
        self.setWindowTitle('ChemBrows')    

#------------------------- CONSTRUCTION DES MENUS -------------------------------------------------------------

        self.menubar = self.menuBar()

        #Building files menu
        self.fileMenu = self.menubar.addMenu('&Files')
        self.fileMenu.addAction(self.exitAction)

        #Building edition menu
        self.editMenu = self.menubar.addMenu("&Edition")
        self.editMenu.addAction(self.parseAction)
        self.editMenu.addAction(self.calculatePercentageMatchAction)
        self.editMenu.addAction(self.likeAction)
        self.editMenu.addAction(self.unLikeAction)

        #Building tools menu
        self.toolMenu = self.menubar.addMenu("&Tools")
        self.toolMenu.addAction(self.openInBrowserAction)

        self.menubar.addAction(self.settingsAction)

        ##Ajout d'une entrée pr les réglages dans la barre
        ##des menus
        #self.menubar.addAction(self.settingsAction)

##------------------------- TOOLBAR  -----------------------------------------------

        ##On crée une zone de recherche et on fixe sa taille
        #self.research_bar = QtGui.QLineEdit()
        #self.research_bar.setFixedSize(self.research_bar.sizeHint())

        #On ajoute une toolbar en la nommant pr l'indentifier,
        #Puis on ajoute les widgets
        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.addAction(self.parseAction)
        self.toolbar.addAction(self.calculatePercentageMatchAction)
        self.toolbar.addAction(self.likeAction)
        self.toolbar.addAction(self.unLikeAction)
        self.toolbar.addAction(self.updateAction)
        self.toolbar.addAction(self.searchNewAction)
        #self.toolbar.addAction(self.verificationAction)
        #self.toolbar.addAction(self.importAction)
        #self.toolbar.addAction(self.putOnWaitingAction)
        #self.toolbar.addAction(self.removeOfWaitingAction)
        #self.toolbar.addAction(self.addTagAction)
        #self.toolbar.addAction(self.removeTagAction)
        #self.toolbar.addAction(self.removeTagAction)
        #self.toolbar.addAction(self.addActorAction)
        #self.toolbar.addAction(self.removeActorAction)
        #self.toolbar.addAction(self.effacerFichierAction)
        #self.toolbar.addWidget(QtGui.QLabel('Rechercher : '))
        #self.toolbar.addWidget(self.research_bar)
        #self.toolbar.addSeparator()

        ##On crée un bouton pr tt remettre à zéro
        self.button_back = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_170_step_backward'), 'Back')
        self.toolbar.addWidget(self.button_back)

        #self.toolbar.addSeparator()

        ##Bouton pour afficher la file d'attente
        #self.button_waiting = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_202_shopping_cart'), "File d'attente")
        #self.toolbar.addWidget(self.button_waiting)

        #self.toolbar.addSeparator()

        ##Bouton pour mélanger
        #self.button_shuffle = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_083_random'), "Shuffle")
        #self.toolbar.addWidget(self.button_shuffle)

        #self.toolbar.addSeparator()

        ##Bouton pr afficher les vids non taguées
        #self.button_untag = QtGui.QPushButton("Non tagué")
        #self.toolbar.addWidget(self.button_untag)


##------------------------- MAIN TABLE ---------------------------------------------------------------------------------------

        self.horizontal_header = QtGui.QHeaderView(QtCore.Qt.Horizontal) #Déclare le header perso
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignLeft) #Aligne à gauche l'étiquette des colonnes
        self.horizontal_header.setClickable(True) #Rend cliquable le header perso

        #Resize to content vertically
        self.tableau.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        #Style du tableau
        self.tableau.setHorizontalHeader(self.horizontal_header) #Active le header perso
        self.tableau.hideColumn(0) #Hide id
        self.tableau.hideColumn(2) #Hide doi
        #self.tableau.hideColumn(6) #Hide authors
        self.tableau.hideColumn(7) #Hide abstracts
        self.tableau.hideColumn(8) #Hide abstracts
        self.tableau.hideColumn(10) #Hide urls
        self.tableau.hideColumn(11) #Hide verif
        self.tableau.hideColumn(12) #Hide new
        ##self.tableau.verticalHeader().setDefaultSectionSize(72) # On met la hauteur des cells à la hauteur des thumbs
        ##self.tableau.setColumnWidth(5, 127) # On met la largeur de la colonne des thumbs à la largeur des thumbs - 1 pixel (plus joli)
        self.tableau.setSortingEnabled(True) #Active le tri
        self.tableau.verticalHeader().setVisible(False) #Cache le header vertical
        #self.tableau.verticalHeader().sectionResizeMode(QHeaderView.ResizeToContents)
        self.tableau.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) #Empêche l'édition des cells


##------------------------- LEFT AREA ------------------------------------------------------------------------

        #On crée un widget conteneur pour les tags
        #self.vbox_journals = QtGui.QVBoxLayout()
        #self.dock_journals = QtGui.QWidget()
        #self.dock_journals.setLayout(self.vbox_journals)

        #On crée des scrollarea pr mettre les boutons des tags et des acteurs
        self.scroll_tags = QtGui.QScrollArea()

        #On crée la zone de scrolling
        #http://www.mattmurrayanimation.com/archives/tag/how-do-i-use-a-qscrollarea-in-pyqt
        self.scrolling_tags = QtGui.QWidget()
        self.vbox_all_tags = QtGui.QVBoxLayout()
        self.scrolling_tags.setLayout(self.vbox_all_tags)


##------------------------- RIGHT BOTTOM AREA ---------------------------------------------------------------------------

        #The bottom area contains the mosaic (graphical abstract)

        #The bottom are is a simple widget
        self.area_right_bottom = QtGui.QWidget()

        #Personnal graphicsView. Allows the resizing of the mosaic
        self.vision = GraphicsViewPerso(self.area_right_bottom)
        self.vision.setDragMode(GraphicsViewPerso.ScrollHandDrag)

        self.box_mosaic = QtGui.QVBoxLayout()
        self.box_mosaic.addWidget(self.vision)

        self.area_right_bottom.setLayout(self.box_mosaic)

#------------------------- RIGHT TOP AREA ------------------------------------------------------------------------------------

        #Creation of a gridLayout to handle the top right area
        self.area_right_top = QtGui.QWidget()
        self.grid_area_right_top = QtGui.QGridLayout()
        self.area_right_top.setLayout(self.grid_area_right_top)

        #Here I set a prelabel: a label w/ just "Title: " to label the title.
        #I set the sizePolicy of this prelabel to the minimum. It will stretch to
        #the minimum. Makes the display better with the grid
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

        #A QWebView to render the sometimes rich text of the abstracts
        self.text_abstract = QtWebKit.QWebView()
        self.web_settings = QtWebKit.QWebSettings.globalSettings()
        self.web_settings.setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 20)

        #Building the grid
        self.grid_area_right_top.addWidget(prelabel_title, 0, 0)
        self.grid_area_right_top.addWidget(self.label_title, 0, 1)
        self.grid_area_right_top.addWidget(prelabel_author, 1, 0)
        self.grid_area_right_top.addWidget(self.label_author, 1, 1)
        self.grid_area_right_top.addWidget(self.text_abstract, 2, 0, 1, 2)

##------------------------- ASSEMBLING THE AREAS ------------------------------------------------------------------------------------

        #Main part of the window in a tab.
        #Allows to create other tabs
        self.onglets = QtGui.QTabWidget()
        self.onglets.addTab(self.tableau, "All articles")

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter1.addWidget(self.area_right_top)
        self.splitter1.addWidget(self.area_right_bottom)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter2.addWidget(self.scroll_tags)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.splitter1)

        self.setCentralWidget(self.splitter2)    

        self.show()


if __name__ == '__main__':

    #Little hack to kill all the pending process
    os.setpgrp() # create new process group, become its leader
    try:
        app = QtGui.QApplication(sys.argv)
        ex = Fenetre()
        sys.exit(app.exec_())
    finally:
        os.killpg(0, signal.SIGKILL) # kill all processes in my group

