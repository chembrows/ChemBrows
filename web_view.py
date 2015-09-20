#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtGui, QtCore, QtWebKit


class WebViewPerso(QtWebKit.QWebView):

    """Zoomable QWebView"""

    def __init__(self, parent=None):

        super(WebViewPerso, self).__init__(parent)
        self.parent = parent

        # Attribute to store the background state: dark or light
        self.dark = 0

        self.x = 0
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)

        # Get the default font and use it for the QWebView
        self.settings().setFontFamily(QtWebKit.QWebSettings.StandardFont, self.font().family())


    def darkAndLight(self):

        """Change the background and the font colors of the abstract
        reading area, through a boolean"""

        self.dark = 1 - self.dark
        self.setHtml()


    def setHtml(self, string=None):

        """Re-implementation of the parent method"""

        if string is None:
            string = self.page().mainFrame().toHtml().split("</style>")[-1]

        # Change the background and font colors
        if self.dark == 1:
            self.setStyleSheet("background-color: grey;")
            string = "<style>body {color:white}</style>" + string
        else:
            self.setStyleSheet("background-color: white;")
            string = "<style>body {color:black}</style>" + string

        super().setHtml(string)


    def zoom(self, more_or_less):

        """Zoom in or out when the user clicks the buttons in the
        article toolbar"""

        if more_or_less:
            increment = 1
        else:
            increment = -1

        self.x += increment * 0.25

        self.setZoomFactor(1 + self.x / 10)


    def wheelEvent(self, event):

        """Subclassing mouse wheel event
        http://www.codeprogress.com/cpp/libraries/qt/showQtExample.php?index=416&key=QWebViewZoomINOUT
        """

        super(WebViewPerso, self).wheelEvent(event)

        modifiers = QtGui.QApplication.keyboardModifiers()

        # # Zoom only if ctrl is pressed
        if modifiers == QtCore.Qt.ControlModifier:
            self.x += float(event.delta() / 120)
            print(self.x)
            print(1 + self.x /10)
            self.setZoomFactor(1 + self.x / 10)
