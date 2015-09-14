#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt4 import QtGui, QtCore
import random
import re
import requests

from functions import simpleChar


class Signing(QtGui.QDialog):

    """Module to log the user and assign to him a user_id
    the first he starts the programm"""

    def __init__(self, parent):

        super(Signing, self).__init__(parent)

        self.parent = parent

        self.setModal(True)

        self.initUI()
        self.defineSlots()


    def askQuestion(self):

        questions = [
                     ('What animal has a trunk ?', 'elephant'),
                     ('How many continents are there ?', '6'),
                     ('Where is Big Ben ?', 'london')
                    ]
        question = questions[random.randint(0, len(questions) - 1)]
        self.answer = question[1]

        return question[0]


    def defineSlots(self):

        """Establish the slots"""

        # If OK pressed, send a request to the server
        self.ok_button.clicked.connect(self.validateForm)

        # If Cancel is pressed, terminate the program. The user can't
        # use it if he's not logged
        self.cancel_button.clicked.connect(self.parent.closeEvent)


    def validateForm(self):

        # http://sametmax.com/valider-une-adresse-email-avec-une-regex-en-python/

        validate = True

        email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)

        if email_re.search(self.line_email.text()) is None:
            self.line_email.setStyleSheet('QLineEdit {background-color: #FFA07A}')
            validate = False
        else:
            self.line_email.setStyleSheet(None)

        if self.combo_status.currentIndex() == 0:
            self.combo_status.setStyleSheet('QComboBox {background-color: #FFA07A}')
            validate = False
        else:
            self.combo_status.setStyleSheet(None)

        user_answer = simpleChar(self.line_question.text())

        if user_answer != self.answer:
            self.line_question.setStyleSheet('QLineEdit {background-color: #FFA07A}')
            validate = False
            self.form_sign.labelForField(self.line_question).setText(self.askQuestion())
        else:
            self.line_question.setStyleSheet(None)

        # TODO: transformer statut en nombre

        if validate:
            payload = {
                       'status': self.combo_status.currentIndex(),
                       'email': self.line_email.text(),
                      }

            # payload = {
                       # 'status': 0,
                       # 'email': 'jp@um2.fr',
                      # }
            try:
                r = requests.post("http://chembrows.com/cgi-bin/sign.py", params=payload)
            except requests.exceptions.ReadTimeout:
                QtGui.QMessageBox.critical(self, "Signing up error", "An time out error occured while contacting the server. \
                        Please check you are connected to the internet, or contact us.",
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
                self.parent.l.critical("ReadTimeout error while contacting the server. No signing up.")
            except requests.exceptions.ConnectionError:
                QtGui.QMessageBox.critical(self, "Signing up error", "An error occured while contacting the server. \
                        Please check you are connected to the internet, or contact us.",
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
                self.parent.l.critical("ConnectionError error while contacting the server. No signing up.")

            # r = requests.post("http://127.0.0.1:8000/cgi-bin/test.py", data=payload)


            response = [part for part in r.text.split("\n") if part != '']

            if 'user_id' in response[-1]:
                self.parent.options.setValue('user_id', response[-1].split(':')[-1])
                self.close()
                del self
            elif response[-1] == 'A user with this email already exists':
                QtGui.QMessageBox.critical(self, "Signing up error", "A user with the same email already exists. Please use another email or contact us.",
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)

            # TODO: gérer le cas où le serveur réponde "Wrong data". Peu probable


    def initUI(self):

        """Handles the display"""

        self.combo_status = QtGui.QComboBox()
        self.combo_status.addItem(None)
        self.combo_status.addItem("Student")
        self.combo_status.addItem("PhD student")
        self.combo_status.addItem("Post doc")
        self.combo_status.addItem("Researcher")
        self.combo_status.addItem("Professor")
        self.combo_status.addItem("Obi Wan Kenobi")

        self.form_sign = QtGui.QFormLayout()

        self.form_sign.addRow("What are you? :", self.combo_status)

        self.line_email = QtGui.QLineEdit(self)

        self.form_sign.addRow("Email :", self.line_email)

        self.line_question = QtGui.QLineEdit()
        self.line_question.setPlaceholderText("Prove you are human !")
        self.form_sign.addRow(self.askQuestion(), self.line_question)

        self.ok_button = QtGui.QPushButton("OK", self)
        self.cancel_button = QtGui.QPushButton("Cancel", self)

        self.hbox_buttons = QtGui.QHBoxLayout()
        self.vbox_global = QtGui.QVBoxLayout()

        self.hbox_buttons.addWidget(self.cancel_button)
        self.hbox_buttons.addWidget(self.ok_button)

        self.vbox_global.addLayout(self.form_sign)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)
        self.show()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    parent = QtGui.QWidget()
    obj = Signing(parent)
    sys.exit(app.exec_())
