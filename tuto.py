#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets

import functions


class Tuto(QtWidgets.QDialog):

    """Module to show a tutorial. It will guide the user
    trough the use of ChemBrows"""

    def __init__(self, parent=None):

        super(Tuto, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.parent = parent
        self.resource_dir, self.DATA_PATH = functions.getRightDirs()

        if parent is None:
            self.test = True
        else:
            self.test = False

        self.setModal(True)

        # Get the text of the slides from config files
        with open(os.path.join(self.resource_dir, 'config/tuto.txt'),
                  'r') as f:
            content = f.read()
            self.list_slides = content.split('--')

        # Index of the slide
        self.index = 0

        self.initUI()
        self.defineSlots()


    def changeSlide(self, increment):

        """Slot to change the slide"""

        self.index += increment

        try:
            tuto_run = self.parent.options.value("tuto_run", None)
        except AttributeError:
            tuto_run = False

        # Show or hide the combo_box
        if self.index == 1 and not tuto_run:
            self.combo_choice.show()
        else:
            self.combo_choice.hide()

        if self.index == 2 and not tuto_run:
            # Get the choice of field from the user
            choice = self.combo_choice.currentText()

            if not self.test:
                if choice == 'All':
                    self.parent.options.remove("journals_to_parse")
                else:
                    # Set the journals to parse options of the parent
                    with open(os.path.join(self.resource_dir, 'config/fields/{0}'.format(choice)), 'r') as config:
                        self.parent.options.setValue("journals_to_parse",
                                                      [line.rstrip() for line in config])


                # Update the journals buttons on the left dock
                self.parent.displayTags()
                self.parent.resetView()

        # Some conditions to properly set the text of the tuto, when
        # the last and the first slides are displayed. Also changes the
        # buttons when it has to
        if self.index <= 0:
            text = self.parseSlide(self.list_slides[0])
            self.previous_button.setEnabled(False)
        elif self.index >= len(self.list_slides) - 1:
            text = self.parseSlide(self.list_slides[-1])
            self.next_button.setEnabled(False)
            self.quit_button.setText("Finish")
        else:
            text = self.parseSlide(self.list_slides[self.index])
            self.next_button.setEnabled(True)
            self.previous_button.setEnabled(True)
            self.quit_button.setText("Quit tuto")

        self.text_diapo.setText(text)


    def finishTuto(self):

        """Slot called when the tuto is finnished or quitted"""

        # Create a bool to check if the user has already run the tuto
        if not self.test:
            self.parent.options.setValue("tuto_run", True)


    def parseSlide(self, text):

        """Method to parse the content of the slides. Will automatically
        detect images"""

        try:
            path = os.path.join(self.resource_dir, 'images/',
                                text.split('!!!')[1].rstrip())
            image = QtGui.QPixmap(path)
            image = image.scaledToWidth(60, QtCore.Qt.SmoothTransformation)
            self.label_image.setPixmap(image)
            self.label_image.show()
            return text.split('!!!')[0]
        except IndexError:
            self.label_image.hide()
            self.adjustSize()
            return text


    def defineSlots(self):

        """Establish the slots"""

        # If next pressed, go to next slide
        self.next_button.clicked.connect(lambda: self.changeSlide(1))

        # If previous pressed, go to previous slide
        self.previous_button.clicked.connect(lambda: self.changeSlide(-1))

        # Quit the tuto at any moment
        # Connect 2 slots to the quit button bc 'done' needs a return code
        self.quit_button.clicked.connect(self.finishTuto)
        self.quit_button.clicked.connect(self.done)


    def initUI(self):

        """Handles the display"""

        self.setWindowTitle('Tutorial')

        self.text_diapo = QtWidgets.QLabel()
        # Clickable URLs
        self.text_diapo.setOpenExternalLinks(True)

        self.label_image = QtWidgets.QLabel()
        self.label_image.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_image.hide()

        # Parse the images that could be present on the first slide
        text = self.parseSlide(self.list_slides[0])
        self.text_diapo.setText(text)

        choices = ['All'] + sorted(os.listdir(os.path.join(self.resource_dir, 'config/fields/')))
        self.combo_choice = QtWidgets.QComboBox()
        self.combo_choice.addItems(choices)
        self.combo_choice.hide()

        self.quit_button = QtWidgets.QPushButton("Quit tuto", self)
        self.previous_button = QtWidgets.QPushButton("Previous", self)
        self.next_button = QtWidgets.QPushButton("Next", self)

        self.previous_button.setEnabled(False)

        self.hbox_buttons = QtWidgets.QHBoxLayout()
        self.vbox_global = QtWidgets.QVBoxLayout()

        self.hbox_buttons.addWidget(self.quit_button)
        self.hbox_buttons.addWidget(self.previous_button)
        self.hbox_buttons.addWidget(self.next_button)

        self.vbox_global.addWidget(self.text_diapo)
        self.vbox_global.addWidget(self.label_image)
        self.vbox_global.addWidget(self.combo_choice)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)
        self.show()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    obj = Tuto()
    sys.exit(app.exec_())
