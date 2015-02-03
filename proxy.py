#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtGui


class ProxyPerso(QtGui.QSortFilterProxyModel):

    """Sublclass of the proxy model, because clicking
    on the header in the main window destroys the proxy
    and creates a bug on the sorting"""

    def __init__(self, parent=None):
        super(ProxyPerso, self).__init__(parent)

        self.parent = parent

    def sort(self, column, order):
        super(ProxyPerso, self).sort(column, order)

        # table = self.parent.liste_tables_in_tabs[self.parent.onglets.currentIndex()]
        # model = self.parent.liste_models_in_tabs[self.parent.onglets.currentIndex()]

        # self.parent.proxy.setSourceModel(self.parent.modele)
        # self.parent.tableau.setModel(self.parent.proxy)

        # self.parent.proxy.setSourceModel(model)
        # table.setModel(self.parent.proxy)
