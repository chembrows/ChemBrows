#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt4 import QtGui, QtCore


class Tuto(QtGui.QDialog):

    """Module to show a tutorial. It will guide the user
    trough the use of ChemBrows"""

    def __init__(self, parent):

        super(Tuto, self).__init__(parent)


        self.parent = parent

        if type(parent) is QtGui.QWidget:
            self.test = True
        else:
            self.test = False

        self.setModal(True)

        # Get the text of the slides from config files
        with open('./config/tuto.txt', 'r') as f:
            content = f.read()
            self.list_slides = content.split('--')

        # Index of the slide
        self.index = 0

        self.initUI()
        self.defineSlots()


    def changeSlide(self, increment):

        """Slot to change the slide"""

        self.index += increment

        # Show or hide the combo_box
        if self.index == 1:
            self.combo_choice.show()
        else:
            self.combo_choice.hide()

        if self.index == 2:
            # Get the choice of field from the user
            choice = self.combo_choice.currentText()

            if not self.test:
                if choice == 'All':
                    self.parent.options.remove("journals_to_parse")
                else:
                    # Set the journals to parse options of the parent
                    with open('./config/fields/{0}'.format(choice), 'r') as config:
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
            self.text_diapo.setText(text)

            self.previous_button.setEnabled(False)
        elif self.index >= len(self.list_slides) - 1:
            text = self.parseSlide(self.list_slides[-1])
            self.text_diapo.setText(text)

            self.next_button.setEnabled(False)
            self.quit_button.setText("Finish")
        else:
            text = self.parseSlide(self.list_slides[self.index])
            self.text_diapo.setText(text)

            self.next_button.setEnabled(True)
            self.previous_button.setEnabled(True)
            self.quit_button.setText("Quit tuto")


    def parseSlide(self, text):

        try:
            path = './images/' + text.split('!!!')[1].rstrip()
            self.label_image.show()
            image = QtGui.QPixmap(path)
            image = image.scaledToWidth(60, QtCore.Qt.SmoothTransformation)
            self.label_image.setPixmap(image)
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
        self.quit_button.clicked.connect(self.done)


    def initUI(self):

        """Handles the display"""

        self.setWindowTitle('Tutorial')

        self.text_diapo = QtGui.QLabel()
        # font = self.text_diapo.font()
        # font.setPointSize(11)
        # self.text_diapo.setFont(font)

        self.label_image = QtGui.QLabel()
        self.label_image.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_image.hide()

        # Parse the images that could be present on the first slide
        text = self.parseSlide(self.list_slides[0])
        self.text_diapo.setText(text)

        choices = ['All'] + sorted(os.listdir('./config/fields/'))
        self.combo_choice = QtGui.QComboBox()
        self.combo_choice.addItems(choices)
        self.combo_choice.hide()

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
        self.vbox_global.addWidget(self.label_image)
        self.vbox_global.addWidget(self.combo_choice)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)
        self.show()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    parent = QtGui.QWidget()
    obj = Tuto(parent)
    sys.exit(app.exec_())
