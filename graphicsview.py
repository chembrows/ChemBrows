#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtGui, QtCore


class GraphicsViewPerso(QtGui.QGraphicsView):

    """Classe perso qui permet d'implémenter un zoom pour la mosaïque
    http://stackoverflow.com/questions/12249875/pyqt4-mousepressevent-position-offset-in-qgraphicsview"""
    

    def __init__(self,  parent = None):

        super(GraphicsViewPerso, self).__init__(parent)
        self.parent = parent
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)


    def wheelEvent(self, event):

        """On réimplémente la gestion de la molette"""

        super(GraphicsViewPerso, self).wheelEvent(event)

        modifiers = QtGui.QApplication.keyboardModifiers()

        #On zoome seulement si la touche Ctrl est enfoncée
        if modifiers == QtCore.Qt.ControlModifier:
            self.setTransformationAnchor(GraphicsViewPerso.AnchorUnderMouse)
            factor = 1.2
            if event.delta() < 0 :
                factor = 1.0 / factor
            self.scale(factor, factor)
