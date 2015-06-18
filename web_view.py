#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtGui, QtCore, QtWebKit


class WebViewPerso(QtWebKit.QWebView):

    """Zoomable QWebView"""

    def __init__(self, parent=None):

        super(WebViewPerso, self).__init__(parent)
        self.parent = parent

        self.x = 0
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)


    def wheelEvent(self, event):

        """Subclassing mouse wheel event
        http://www.codeprogress.com/cpp/libraries/qt/showQtExample.php?index=416&key=QWebViewZoomINOUT
        """

        super(WebViewPerso, self).wheelEvent(event)

        modifiers = QtGui.QApplication.keyboardModifiers()

        # # Zoom only if ctrl is pressed
        if modifiers == QtCore.Qt.ControlModifier:
            self.x += float(event.delta() / 120)
            self.setZoomFactor(1 + self.x / 10)
