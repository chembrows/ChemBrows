#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore

#import liste

class ModelPerso(QtSql.QSqlTableModel):

    """On sous-classe le modèle pour charger toute la
    bdd en une seule fois. Peut causer des problèmes de
    performance."""

    #def __init__(self, parent=None, database=None):
    def __init__(self):
        super(ModelPerso, self).__init__()

    
    def setQuery(self, query):

        """Réimplémentation de cette méthode. Elle permet dorénavant
        de charger ts les résultats retournés par la requêteen une
        seule fois. Peut causer des problèmes de performances"""
        #http://stackoverflow.com/questions/17879013/
        #reimplementing-qsqltablemodel-setquery

        #self.setTable("videos")

        self.query = QtSql.QSqlQuery()

        #On rééxécute la requête car la bdd a potentiellement
        #été modifiée
        self.query.prepare(query.executedQuery())
        self.query.exec_()

        results = QtSql.QSqlTableModel.setQuery(self, self.query)

        #self.setHeaderData(5, QtCore.Qt.Horizontal, "", QtCore.Qt.DisplayRole)
        #self.setHeaderData(6, QtCore.Qt.Horizontal, "Modification")
        #self.setHeaderData(9, QtCore.Qt.Horizontal, "Ajout")

        while self.canFetchMore():
            self.fetchMore()
        return results


    def select(self):

        """Réimplémentation de cette méthode. Elle permet dorénavant
        de charger tte la bdd en une seule fois. Peut causer des problèmes
        de performances"""
        #http://www.developpez.net/forums/d1243418/autres-langages/
        #python-zope/gui/pyside-pyqt/reglage-ascenseur-vertical-qtableview/

        #self.setTable("videos")

        results = QtSql.QSqlTableModel.select(self)

        while self.canFetchMore():
            self.fetchMore()
        return results
