#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtGui, QtCore


class ButtonLineEdit(QtGui.QLineEdit):
    # http://stackoverflow.com/questions/12462562/how-to-do-inside-in-qlineedit-insert-the-button-pyqt4

    buttonClicked = QtCore.pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):

        super(ButtonLineEdit, self).__init__(parent)

        self.button = QtGui.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.buttonClicked.emit)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth * 2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth * 2 + 2))


    def resizeEvent(self, event):

        # self.button.setIconSize(QtCore.QSize(self.button.width() / 2, self.button.height() / 2))
        self.button.setIconSize(QtCore.QSize(self.button.height() / 2, self.button.width() / 2))

        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth * 6 - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1) / 2)


        super(ButtonLineEdit, self).resizeEvent(event)

