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
from tabwidget import TabPerso
from worker import Worker
from predictor import Predictor
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

        self.connectionBdd()
        self.defineActions()
        self.initUI()
        self.defineSlots()
        self.restoreSettings()


    def connectionBdd(self):

        """Méthode qui se connecte à la bdd, crée un modèle, et l'associe
        à la vue"""

        #Accès à la base de donnée.
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName("fichiers.sqlite")
        self.bdd.open()

        query = QtSql.QSqlQuery("fichiers.sqlite")
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                     doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                     liked INTEGER, url TEXT, verif INTEGER)")


        #Création du modèle, issu de la bdd
        self.modele = ModelPerso()

        #On change la stratégie d'édition de la bdd, les changements
        #sont immédiats
        self.modele.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.modele.setTable("papers")
        self.modele.select() # Remplit le modèle avec les data de la table

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


    def parse(self):

        """Method to start the parsing of the data"""

        #flux = ["ang.xml", "jacs.xml"]
        #flux = ["http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773",
                #"http://feeds.feedburner.com/acs/jacsat"
               #]

        #flux = [
                #"http://feeds.feedburner.com/acs/jacsat"
               #]
        #RSC
        #flux = ["http://feeds.rsc.org/rss/nj"]
        #flux = ["http://feeds.rsc.org/rss/sc"]
        #flux = ["http://feeds.rsc.org/rss/cc"]
        #flux = ["http://feeds.rsc.org/rss/cs"]
        #http://feeds.rsc.org/rss/rp
        #http://feeds.rsc.org/rss/ra

        #ACS
        flux = ["http://feeds.feedburner.com/acs/jceda8"]
        flux = ["http://feeds.feedburner.com/acs/joceah"]


        #Disabling the parse action to avoid double start
        self.parseAction.setEnabled(False)

        #List to store the threads.
        #The list is cleared when the method is started
        self.list_threads = []

        for site in flux:
            #One worker for each website
            worker = Worker(site, self.l)
            worker.finished.connect(self.checkThreads)
            self.list_threads.append(worker)


    def checkThreads(self):

        """Method to check the state of each worker.
        If all the workers are finished, enable the parse action"""

        #Update the view when a worker is finished
        self.modele.select()

        #Get a list of the workers states
        list_states = [ worker.isFinished() for worker in self.list_threads ]

        if not False in list_states:
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

        self.updateAction = QtGui.QAction('Update model', self)
        self.updateAction.triggered.connect(lambda: self.modele.select())
        self.updateAction.setShortcut('F7')

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

        pass


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


    def defineSlots(self):

        """Méthode pour connecter les signaux aux slots. On sépare cette
        partie de la création de la fenêtre pour plus de lisibilité"""

        ##On connecte le signal de double clic sur une cell vers un
        ##slot qui lance le lecteur ac le nom du fichier en paramètre
        #self.tableau.doubleClicked.connect(self.launchFile)

        ##http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        ##Le clic droit est perso
        #self.tableau.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.tableau.customContextMenuRequested.connect(self.popup)

        self.tableau.clicked.connect(self.displayInfos)
        self.tableau.clicked.connect(self.displayMosaic)


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

        pass


    def displayInfos(self):

        try:
            #On essaie de récupérer la description du torrent
            #self.text_abstract.setText(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 7).data())
            self.text_abstract.setHtml(self.tableau.model().index(self.tableau.selectionModel().selection().indexes()[0].row(), 7).data())
        except TypeError:
            self.l.debug("No abstract for this post, displayInfos()")
            self.text_abstract.setHtml("")


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
        self.proxy.setSourceModel(self.modele)
        self.tableau.setModel(self.proxy)

        #self.adjustView()

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

        #On règle les paramètres de la fenêtre
        self.setGeometry(0, 25, 1900 , 1020)
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
        #self.button_back = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_171_fast_backward'), 'Retour')
        #self.toolbar.addWidget(self.button_back)

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


##------------------------- TABLEAU CENTRAL ---------------------------------------------------------------------------------------

        self.horizontal_header = QtGui.QHeaderView(QtCore.Qt.Horizontal) #Déclare le header perso
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignLeft) #Aligne à gauche l'étiquette des colonnes
        self.horizontal_header.setClickable(True) #Rend cliquable le header perso

        ##Resize to content vertically
        #self.tableau.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        #Style du tableau
        self.tableau.setHorizontalHeader(self.horizontal_header) #Active le header perso
        self.tableau.hideColumn(0) #Cache la colonne des id
        #self.tableau.hideColumn(2) #Cache la colonne des doi
        #self.tableau.hideColumn(6) #Cache la colonne des auteurs
        #self.tableau.hideColumn(7) #Cache la colonne des abstracts
        #self.tableau.hideColumn(8) #Cache la colonne des graphical abstracts
        self.tableau.hideColumn(10) #Cache la colonne des urls
        self.tableau.hideColumn(11) #Cache la colonne des verif
        ##self.tableau.verticalHeader().setDefaultSectionSize(72) # On met la hauteur des cells à la hauteur des thumbs
        ##self.tableau.setColumnWidth(5, 127) # On met la largeur de la colonne des thumbs à la largeur des thumbs - 1 pixel (plus joli)
        self.tableau.setSortingEnabled(True) #Active le tri
        self.tableau.verticalHeader().setVisible(False) #Cache le header vertical
        #self.tableau.verticalHeader().sectionResizeMode(QHeaderView.ResizeToContents)
        self.tableau.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) #Empêche l'édition des cells


##------------------------- ZONE DE GAUCHE ------------------------------------------------------------------------

        #On crée un widget conteneur pour les tags
        self.vbox_journals = QtGui.QVBoxLayout()
        self.dock_journals = QtGui.QWidget()
        self.dock_journals.setLayout(self.vbox_journals)

##------------------------- ZONE DU BAS ---------------------------------------------------------------------------

        #On crée la zone du bas, un simple widget
        self.zone_bas = QtGui.QWidget()

        #On utilise un layout pr pouvoir redimensionner
        #la zone de mosaïque automatiquement
        self.vision = GraphicsViewPerso(self.zone_bas)
        self.vision.setDragMode(GraphicsViewPerso.ScrollHandDrag)

        self.box_mosaic = QtGui.QVBoxLayout()
        self.box_mosaic.addWidget(self.vision)

        self.zone_bas.setLayout(self.box_mosaic)

#------------------------- ZONE DE DROITE ------------------------------------------------------------------------------------

        self.text_abstract = QtWebKit.QWebView()
        self.web_settings = QtWebKit.QWebSettings.globalSettings()
        self.web_settings.setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 20)

##------------------------- ASSEMBLAGE DES ZONES------------------------------------------------------------------------------------

        #On définit un TabWidget pr la zone centrale.
        #Cela permettra aux plugins d'ouvrir des onglets.
        self.onglets = QtGui.QTabWidget()
        self.onglets = TabPerso()
        self.onglets.addTab(self.tableau, "New posts")

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter1.addWidget(self.text_abstract)
        self.splitter1.addWidget(self.zone_bas)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter2.addWidget(self.dock_journals)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.splitter1)

        self.setCentralWidget(self.splitter2)    

        self.show()


if __name__ == '__main__':

    #Petit hack qui permet de tuer ts 
    #les subprocesses du programme
    os.setpgrp() # create new process group, become its leader
    try:
        app = QtGui.QApplication(sys.argv)
        ex = Fenetre()
        sys.exit(app.exec_())
    finally:
        os.killpg(0, signal.SIGKILL) # kill all processes in my group

