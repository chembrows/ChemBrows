#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtGui, QtSql, QtCore
import time
import parse

class Worker(QtCore.QThread):

    """Cette classe hérite de QThread pr pouvoir lancer
    l'actualisation des torrents dans un thread à part.
    Cela permet de ne pas faire freezer le programme tout entier
    lors des requêtes http, qui peuvent être longues"""

    #Explique comment faire une classe de thread pr ne pas bloquer la GUI principale
    #http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt


    def __init__(self, window):

        QtCore.QThread.__init__(self, window)

        self.exiting = False

        #On crée un argument pr la fenêtre principale
        self.window = window

        self.window.l.debug("Initialisation du plugin TPB terminée")


    def render(self):

        """Envoyer les paramètres à cette fct !!!"""
        self.start()


    def __del__(self):
    
        self.exiting = True
        self.wait()


    def run(self):

        """Méthode avec l'algo principal de parsing.
        S'appelle run car on sous-classe la méthode run
        de QThread"""

        parse.parse(self.window.l)

        #count = 0
        #while count < 500:
            #time.sleep(1)
            #print("Increasing")
            #count += 1

