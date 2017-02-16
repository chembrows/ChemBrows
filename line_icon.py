#!/usr/bin/python
# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWidgets


class ButtonLineIcon(QtWidgets.QLineEdit):
    # http://stackoverflow.com/questions/12462562/how-to-do-inside-in-qlineedit-insert-the-button-pyqt4

    buttonClicked = QtCore.pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):

        super(ButtonLineIcon, self).__init__(parent)

        # Create a button and connect it to the clear method
        self.button = QtWidgets.QToolButton(self)
        self.button.clicked.connect(self.buttonClicked.emit)
        self.button.setCursor(QtCore.Qt.PointingHandCursor)

        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.setIcon(QtGui.QIcon(icon_file))

        # # Remove the elements of a button: border, background
        self.button.setStyleSheet("background: transparent; border: none;")

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.button, 0, QtCore.Qt.AlignRight)
        self.setTextMargins(0, 0, self.button.sizeHint().width(), 0)
        # layout.setMargin(5)
