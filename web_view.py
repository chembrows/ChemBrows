#!/usr/bin/python
# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWebEngineWidgets, QtWidgets


class WebViewPerso(QtWebEngineWidgets.QWebEngineView):

    """Zoomable QWebView"""

    def __init__(self, parent=None):

        super(WebViewPerso, self).__init__(parent)
        self.parent = parent

        # String to store the content of the 'web page'. Avoids multiple calls
        # to toHtml
        self.content = ""

        self.x = 0
        # self.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.setRenderHint(QtGui.QPainter.TextAntialiasing)

        # Get the default font and use it for the QWebView
        self.settings().setFontFamily(
            QtWebEngineWidgets.QWebEngineSettings.StandardFont,
            self.font().family())

        # Disable following links
        # self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        # self.triggerPageAction(QtWebEngineWidgets.QWebEnginePage.NoWebAction)


    def contextMenuEvent(self, e):

        """Disable right click"""

        pass


    def darkAndLight(self):

        """Change the background and the font colors of the abstract
        reading area, through a boolean"""

        self.parent.dark = 1 - self.parent.dark
        self.setHtml()


    def setHtml(self, string=None):

        """Re-implementation of the parent method"""

        if string is None:
            string = self.content.split("</style>")[-1]
        else:
            self.content = string

        # Change the background and font colors
        if self.parent.dark == 1:
            self.page().setBackgroundColor(QtGui.QColor('grey'))
            string = "<style>body {color:white}</style>" + string
        else:
            self.page().setBackgroundColor(QtGui.QColor('white'))
            string = "<style>body {color:black}</style>" + string

        # Disable/enable the view bc call to setHtml grabs focus. See:
        # https://bugreports.qt.io/browse/QTBUG-52999
        # This bug should be fixed in PyQT 5.7.1
        self.setEnabled(False)

        # Need to set a base url of 'qrc:/' when you call setHtml.
        # http://www.qtcentre.org/threads/34091-QWebView-with-css-js-and-images-in-a-resource-file
        super().setHtml(string, QtCore.QUrl('qrc:/'))

        self.setEnabled(True)


    def zoom(self, more_or_less):

        """Zoom in or out when the user clicks the buttons in the
        article toolbar"""

        if more_or_less:
            increment = 1
        else:
            increment = -1

        self.x += increment * 0.5

        self.setZoomFactor(1 + self.x / 10)


    def wheelEvent(self, event):

        """Subclassing mouse wheel event
        http://www.codeprogress.com/cpp/libraries/qt/showQtExample.php?index=416&key=QWebViewZoomINOUT
        """

        super(WebViewPerso, self).wheelEvent(event)

        modifiers = QtWidgets.QApplication.keyboardModifiers()

        # Zoom only if ctrl is pressed
        if modifiers == QtCore.Qt.ControlModifier:
            self.x += event.angleDelta().y() / 120
            self.setZoomFactor(1 + self.x / 10)
