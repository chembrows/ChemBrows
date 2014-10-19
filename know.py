#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import signal
import numpy as np
import feedparser

from PyQt4 import QtGui, QtSql, QtCore

#Personal modules
from log import MyLog
from model import ModelPerso
from view import ViewPerso
from view_delegate import ViewDelegate
from tabwidget import TabPerso
from worker import Worker


sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt


class Fenetre(QtGui.QMainWindow):
    

    def __init__(self):

        super(Fenetre, self).__init__()
        self.l = MyLog()
        self.l.info('Démarrage du programme')

        self.connectionBdd()
        self.defineActions()
        self.initUI()
        #self.etablirSlots()
        #self.restoreSettings()


    def connectionBdd(self):

        """Méthode qui se connecte à la bdd, crée un modèle, et l'associe
        à la vue"""

        #Accès à la base de donnée.
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE");
        self.bdd.setDatabaseName("fichiers.sqlite");
        self.bdd.open()
        query = QtSql.QSqlQuery("fichiers.sqlite")
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match TEXT, \
                     title TEXT, date TEXT, journal TEXT, abstract TEXT, graphical_abstract TEXT)")


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
        ##self.adjustView()


    def parse(self):

        print("coucou")

        worker = Worker(self)
        worker.render()

    def defineActions(self):

        """On définit ici les actions du programme. Cette méthode est
        appelée à la création de la classe"""

        #Action pour quitter
        #self.exitAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_063_power'), '&Quitter', self)        
        self.exitAction = QtGui.QAction('&Quitter', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Quitter l'application")
        self.exitAction.triggered.connect(self.closeEvent)

        self.parseAction = QtGui.QAction('&Parser', self)        
        self.parseAction.triggered.connect(self.parse)

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

        ##On enregistre l'état de l'application
        #self.options.beginGroup("Window")
        ##On réinitialise les clés
        #self.options.remove("")

        #self.l.debug("Sauvegarde de l'état de la fenêtre dans options.ini")
        #self.options.setValue("window_geometry", self.saveGeometry())
        #self.options.setValue("window_state", self.saveState())
        #self.options.setValue("header_state", self.tableau.horizontalHeader().saveState())
        #self.options.setValue("onglets_gauche_geometry", self.splitter1.saveState())
        #self.options.setValue("splitter_vertical", self.splitter2.saveState())
        #self.options.setValue("splitter_central", self.splitter3.saveState())

        #self.options.endGroup()


        ##On s'assure que self.options finit ttes ces taches.
        ##Corrige un bug. self.options semble ne pas effectuer
        ##ttes ces tâches immédiatement.
        #self.options.sync()

        QtGui.qApp.quit()

        self.l.info("Fermeture du programme")


    def etablirSlots(self):

        """Méthode pour connecter les signaux aux slots. On sépare cette
        partie de la création de la fenêtre pour plus de lisibilité"""

        ##On connecte le signal de double clic sur une cell vers un
        ##slot qui lance le lecteur ac le nom du fichier en paramètre
        #self.tableau.doubleClicked.connect(self.launchFile)

        ##http://www.diotavelli.net/PyQtWiki/Handling%20context%20menus
        ##Le clic droit est perso
        #self.tableau.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.tableau.customContextMenuRequested.connect(self.popup)

        ##On connecte la sélection d'une ligne à l'affichage des tags d'une vid
        #self.tableau.clicked.connect(self.getTags)

        pass


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



    def initUI(self):               

        """Méthode pour créer la fenêtre et régler ses paramètres"""

        #On règle les paramètres de la fenêtre
        self.setGeometry(0, 25, 1900 , 1020)
        self.setWindowTitle('Knowlegator')    

#------------------------- CONSTRUCTION DES MENUS -------------------------------------------------------------

        self.menubar = self.menuBar()

        ##Construction du menu fichier
        ##Les actions sont définies dans une méthode propre
        self.fileMenu = self.menubar.addMenu('&Fichier')
        self.fileMenu.addAction(self.exitAction)
        #self.fileMenu.addAction(self.importAction)
        #self.fileMenu.addAction(self.verificationAction)
        #self.fileMenu.addAction(self.effacerBddAction)

        ##Construction du menu édition
        #self.editMenu = self.menubar.addMenu("&Édition")
        #self.editMenu.addAction(self.putOnWaitingAction)
        #self.editMenu.addAction(self.removeOfWaitingAction)
        #self.editMenu.addAction(self.emptyWaitingAction)
        #self.editMenu.addAction(self.addTagAction)
        #self.editMenu.addAction(self.removeTagAction)
        #self.editMenu.addAction(self.bigRemoveTagAction)
        #self.editMenu.addAction(self.addActorAction)
        #self.editMenu.addAction(self.removeActorAction)
        #self.editMenu.addAction(self.bigRemoveActorAction)
        #self.editMenu.addAction(self.likeAction)
        #self.editMenu.addAction(self.regeneratePicturesAction)
        #self.editMenu.addAction(self.effacerFichierAction)
        #self.editMenu.addAction(self.deleteFileFromBddAction)

        ##Construction du menu outils, ac ttes les features
        ##spéciales
        #self.toolMenu = self.menubar.addMenu("&Outils")
        #self.toolMenu.addAction(self.shuffleAction)
        #self.toolMenu.addAction(self.displayVidsWithNoTagAction)
        #self.toolMenu.addAction(self.statsAction)

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
        #self.toolbar.addAction(self.verificationAction)
        #self.toolbar.addAction(self.importAction)
        #self.toolbar.addAction(self.putOnWaitingAction)
        #self.toolbar.addAction(self.removeOfWaitingAction)
        #self.toolbar.addAction(self.likeAction)
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
        ##self.tableau.horizontalHeader().setResizeMode(5, QtGui.QHeaderView.Fixed)
        self.tableau.resizeColumnToContents(1) #Redimensionne au contenu des cells

        #Style du tableau
        self.tableau.setHorizontalHeader(self.horizontal_header) #Active le header perso
        ##self.tableau.hideColumn(0) #Cache la colonne des id
        ##self.tableau.hideColumn(2) #Cache la colonne des name_simple
        ##self.tableau.hideColumn(4) #Cache la colonne des path 
        ###self.tableau.hideColumn(6) #Cache la colonne des dates de modification 
        ##self.tableau.hideColumn(7) #Cache la colonne des md4 
        ##self.tableau.hideColumn(10) #Cache la colonne waited
        ##self.tableau.horizontalHeader().moveSection(5, 0) # Met les thumbs en premier
        ##self.tableau.verticalHeader().setDefaultSectionSize(72) # On met la hauteur des cells à la hauteur des thumbs
        ##self.tableau.setColumnWidth(5, 127) # On met la largeur de la colonne des thumbs à la largeur des thumbs - 1 pixel (plus joli)
        self.tableau.setSortingEnabled(True) #Active le tri
        self.tableau.verticalHeader().setVisible(False) #Cache le header vertical
        self.tableau.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) #Empêche l'édition des cells


##------------------------- ZONE DE GAUCHE ------------------------------------------------------------------------

        #On crée un widget conteneur pour les tags
        self.vbox_journals = QtGui.QVBoxLayout()
        self.dock_journals = QtGui.QWidget()
        self.dock_journals.setLayout(self.vbox_journals)

##------------------------- ZONE DU BAS ---------------------------------------------------------------------------

        #On crée la zone du bas, un simple widget
        self.zone_bas = QtGui.QWidget()


##------------------------- ASSEMBLAGE DES ZONES------------------------------------------------------------------------------------

        #On crée un splitter horizontal pour mettre les widgets du haut
        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.dock_journals)

        #On définit un TabWidget pr la zone centrale.
        #Cela permettra aux plugins d'ouvrir des onglets.
        self.onglets = QtGui.QTabWidget()
        self.onglets = TabPerso()
        self.onglets.addTab(self.tableau, "Bibliothèque")

        self.splitter1.addWidget(self.onglets)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.zone_bas)

        #self.splitter3 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        #self.splitter3.addWidget(self.splitter2)
        #self.splitter3.addWidget(self.onglets_droite)

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

