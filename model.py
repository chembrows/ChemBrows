#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore

# import liste

class ModelPerso(QtSql.QSqlTableModel):

    """On sous-classe le modèle pour charger toute la
    bdd en une seule fois. Peut causer des problèmes de
    performance."""

    # def __init__(self, parent=None, database=None):
    def __init__(self):
        super(ModelPerso, self).__init__()


    def setQuery(self, query):

        """Réimplémentation de cette méthode. Elle permet dorénavant
        de charger ts les résultats retournés par la requêteen une
        seule fois. Peut causer des problèmes de performances"""
        # http://stackoverflow.com/questions/17879013/
        # reimplementing-qsqltablemodel-setquery

        self.query = QtSql.QSqlQuery()

        if type(query) is str:
            self.query.prepare(query)
        else:
            self.query.prepare(query.executedQuery())

        self.query.exec_()

        results = QtSql.QSqlTableModel.setQuery(self, self.query)

        while self.canFetchMore():
            self.fetchMore()
        return results


    def select(self):

        """Réimplémentation de cette méthode. Elle permet dorénavant
        de charger tte la bdd en une seule fois. Peut causer des problèmes
        de performances"""
        # http://www.developpez.net/forums/d1243418/autres-langages/
        # python-zope/gui/pyside-pyqt/reglage-ascenseur-vertical-qtableview/

        results = QtSql.QSqlTableModel.select(self)

        while self.canFetchMore():
            self.fetchMore()
        return results
