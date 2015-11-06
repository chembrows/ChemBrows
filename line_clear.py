#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtGui, QtCore


class ButtonLineEdit(QtGui.QLineEdit):
    # http://stackoverflow.com/questions/12462562/how-to-do-inside-in-qlineedit-insert-the-button-pyqt4

    buttonClicked = QtCore.pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):

        super(ButtonLineEdit, self).__init__(parent)

        # Create a button and connect it to the clear method
        self.button = QtGui.QToolButton(self)
        self.button.setCursor(QtCore.Qt.PointingHandCursor)
        self.button.clicked.connect(self.clear)
        self.button.clicked.connect(parent.searchByButton)

        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.setIcon(QtGui.QIcon(icon_file))

        # Remove the elements of a button: border, background
        self.button.setStyleSheet("background: transparent; border: none; margin-top: 5px;")

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.button, 0, QtCore.Qt.AlignRight)
        self.setTextMargins(0, 0, self.button.sizeHint().width(), 0)
        layout.setMargin(5)
