#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt4 import QtGui


class Tuto(QtGui.QDialog):

    """Module to show a tutorial. It will guide the user
    trough the use of ChemBrows"""

    def __init__(self, parent):

        super(Tuto, self).__init__(parent)

        self.parent = parent

        self.setModal(True)

        self.list_slides = []

        # Get the text of the slides from config files
        for slide in sorted(os.listdir("./config/tuto")):
            with open('./config/tuto/{0}'.format(slide), 'r') as f:
                self.list_slides.append(f.read())

        self.initUI()
        self.defineSlots()


    def changeSlide(self, increment):

        """Slot to change the slide"""

        index = self.list_slides.index(self.text_diapo.text())

        index += increment

        # Some conditions to properly set the text of the tuto, when
        # the last and the first slides are displayed. Also changes the
        # buttons when it has to
        if index <= 0:
            self.text_diapo.setText(self.list_slides[0])
            self.previous_button.setEnabled(False)
        elif index >= len(self.list_slides) - 1:
            self.next_button.setEnabled(False)
            self.quit_button.setText("Finish")
            self.text_diapo.setText(self.list_slides[-1])
        else:
            self.next_button.setEnabled(True)
            self.previous_button.setEnabled(True)
            self.quit_button.setText("Quit tuto")
            self.text_diapo.setText(self.list_slides[index])


    def defineSlots(self):

        """Establish the slots"""

        # If next pressed, go to next slide
        self.next_button.clicked.connect(lambda: self.changeSlide(1))

        # If previous pressed, go to previous slide
        self.previous_button.clicked.connect(lambda: self.changeSlide(-1))

        # Quit the tuto at any moment
        self.quit_button.clicked.connect(self.done)


    def initUI(self):

        """Handles the display"""

        self.text_diapo = QtGui.QLabel()
        self.text_diapo.setText(self.list_slides[0])

        self.quit_button = QtGui.QPushButton("Quit tuto", self)
        self.previous_button = QtGui.QPushButton("Previous", self)
        self.next_button = QtGui.QPushButton("Next", self)

        self.previous_button.setEnabled(False)

        self.hbox_buttons = QtGui.QHBoxLayout()
        self.vbox_global = QtGui.QVBoxLayout()

        self.hbox_buttons.addWidget(self.quit_button)
        self.hbox_buttons.addWidget(self.previous_button)
        self.hbox_buttons.addWidget(self.next_button)

        self.vbox_global.addWidget(self.text_diapo)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)
        self.show()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    parent = QtGui.QWidget()
    obj = Tuto(parent)
    sys.exit(app.exec_())
