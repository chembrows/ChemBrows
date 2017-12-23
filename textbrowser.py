#!/usr/bin/python
# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWidgets
from bs4 import BeautifulSoup


class TextBrowserPerso(QtWidgets.QTextBrowser):

    """Zoomable QWebView"""

    def __init__(self, parent=None):

        super(TextBrowserPerso, self).__init__(parent)
        self.parent = parent

        # Disable right click
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        # Initial width of the graphical abstract, in pixels
        self.ini_width = 0

        # Nbr of times the user has zoomed
        self.times = 0


    def resetZoom(self):

        """Reset the zoom"""

        if self.times == 0:
            return
        elif self.times > 0:
            for i in range(self.times):
                self.zoomOut()
        elif self.times < 0:
            for i in range(abs(self.times)):
                self.zoomIn()

        self.times = 0

        # Reset the content so the image can be updated.
        content = self.toHtml()
        self.setHtml("")
        self.setHtml(content)


    def _zoomImage(self, more_or_less: bool):

        """Zoom the grphical abstract"""

        soup = BeautifulSoup(self.toHtml(), "html.parser")

        try:
            # Find the current width of the image
            width = float(soup.findAll('img')[-1]['width'])
            if more_or_less:
                size = width + 0.1 * self.ini_width
            else:
                size = width - 0.1 * self.ini_width

            # Modify the width in the html
            soup.findAll('img')[-1]['width'] = size
        except IndexError:
            # Article has no graphical abstract
            self.parent.l.debug("_zoomImage, no image")

        # Clean the style attribute of the body tag, otherwise zooming is not
        # possible anymore
        soup.body['style'] = ''

        return soup.renderContents().decode()


    def zoom(self, more_or_less: bool):

        """Zoom in or out when the user clicks the buttons in the
        article toolbar"""

        if more_or_less:
            self.zoomIn()
            self.times += 1
        else:
            self.zoomOut()
            self.times -= 1

        content = self._zoomImage(more_or_less)

        # Reset the content so the image can be updated.
        self.setHtml("")
        self.setHtml(content)


    def wheelEvent(self, event):

        """Subclassing mouse wheel event
        http://www.codeprogress.com/cpp/libraries/qt/showQtExample.php?index=416&key=QWebViewZoomINOUT
        """

        modifiers = QtWidgets.QApplication.keyboardModifiers()

        # Zoom only if ctrl is pressed
        if modifiers == QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn()
                self.times += 1
                content = self._zoomImage(True)
            elif event.angleDelta().y() < 0:
                self.zoomOut()
                self.times -= 1
                content = self._zoomImage(False)

            # Reset the content so the image can be updated.
            # https://bugreports.qt.io/browse/QTBUG-54375
            self.setHtml("")
            self.setHtml(content)
        else:
            super(TextBrowserPerso, self).wheelEvent(event)


    def loadResource(self, type: int, name: QtCore.QUrl):

        """Reimplemented to load graphical abstracts w/ good quality
        http://forum.qtfr.org/discussion/2211/qt4-afficher-un-qimage-dans-qtextbrowser
        """

        if type != QtGui.QTextDocument.ImageResource:
            return

        soup = BeautifulSoup(self.toHtml(), "html.parser")

        try:
            # Find the current width of the image
            width = float(soup.findAll('img')[-1]['width'])
            # Load image w/ SmoothTransformation
            image = QtGui.QPixmap(name.path())
            image = image.scaledToWidth(width,
                                        QtCore.Qt.SmoothTransformation)

            self.document().addResource(QtGui.QTextDocument.ImageResource,
                                        name, image)
        except Exception as e:
            self.parent.l.debug("loadResource: {}, likely not a good image".
                                format(e))


    def setSource(self, name: QtCore.QUrl):

        """Reimplemented to disable links in the abstract"""

        return
