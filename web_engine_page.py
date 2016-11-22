#!/usr/bin/python
# coding: utf-8

# http://stackoverflow.com/questions/40747827/qwebenginepage-disable-links/40748293#40748293

from PyQt5 import QtWebEngineWidgets


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

    """
    Class reimplementation, to disable link navigation.
    Replacement of PyQt4's setLinkDelegationPolicy policy.
    """

    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__(parent)

    def acceptNavigationRequest(self, url, navtype, mainframe):

        """Disable navigation"""

        return False


if __name__ == '__main__':
    pass
