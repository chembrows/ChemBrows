#!/usr/bin/python
# coding: utf-8


from PyQt4 import QtSql


class ModelPerso(QtSql.QSqlTableModel):

    """Subclassing the model to sort the data at will"""

    def __init__(self, parent):
        super(ModelPerso, self).__init__(parent)

        self.parent = parent


    def setQuery(self, query):

        """Reimplementation. Allows to load all the data at once, for a query.
        Can cause performance issues"""
        # http://stackoverflow.com/questions/17879013/
        # reimplementing-qsqltablemodel-setquery

        self.query = QtSql.QSqlQuery()

        # If the user has checked the reverse order
        if self.parent.sorting_reversed:
            reverse = "ASC"
        else:
            reverse = "DESC"

        # Sorting method wanted by the user
        if self.parent.sorting_method == 1:
            sorting = "date"
            str_sorting = " ORDER BY {} {}".format(sorting, reverse)
        else:
            sorting = "percentage_match"
            str_sorting = " ORDER BY {} {}".format(sorting, reverse)

        if type(query) is str:
            self.query.prepare(query + str_sorting)
        else:
            self.query.prepare(query.executedQuery() + str_sorting)

        self.query.exec_()

        results = QtSql.QSqlTableModel.setQuery(self, self.query)

        return results
