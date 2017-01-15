#!/usr/bin/python
# coding: utf-8


import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import os
import requests
from io import BytesIO
import base64
from PIL import Image
import platform

from line_icon import ButtonLineIcon
from log import MyLog
import functions


class Signing(QtWidgets.QDialog):

    """Module to log the user and assign to him a user_id
    the first time he starts the programm"""

    def __init__(self, parent=None):

        super(Signing, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.parent = parent

        self.resource_dir, self.DATA_PATH = functions.getRightDirs()


        if parent is None:
            self.logger = MyLog("activity.log")
            self.test = True
        else:
            self.logger = self.parent.l
            self.test = False

        # Attribute to check if the login was valid
        self.validated = False

        self.setModal(True)

        self.initUI()
        self.defineSlots()
        self.getCaptcha()


    def closeEvent(self, event):

        """Actions to perform when closing the window.
        Exit ChemBrows if the user closes this window"""

        self.parent.close()

        # Close the app if the user does not signin
        if not self.validated and not self.test:
            self.logger.critical("The user did not sign in")
            self.parent.closeEvent(event)


    def showInfo(self):

        """Open a dialog info box to tell the user what we are
        using his email for"""

        mes = """
        Your email address will ONLY be used to provide you with \
        important news about ChemBrows (ex: updates)
        """.replace('    ', '')

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")

        QtWidgets.QMessageBox.information(self, "Information", mes,
                                      QtWidgets.QMessageBox.Ok)


    def getCaptcha(self):

        # r = requests.get("http://127.0.0.1:8000/cgi-bin/cap.py")
        # remove b'' of the str representation of the bytes
        # only for local server
        # self.captcha_id = r.text.split('\n')[0][2:][:-1]
        # text = r.text.split('\n')[1][2:][:-1]

        r = requests.get("http://chembrows.com/cgi-bin/cap.py")
        self.captcha_id = r.text.split('\n')[0]
        text = r.text.split('\n')[1]

        io = BytesIO(base64.b64decode(text))
        Image.open(io).save(os.path.join(self.DATA_PATH,
                                         'captcha.png'), format='PNG')

        image = QtGui.QPixmap(os.path.join(self.DATA_PATH,
                                           'captcha.png'))
        self.label_image.setPixmap(image)


    def defineSlots(self):

        """Establish the slots"""

        # If OK pressed, send a request to the server
        self.ok_button.clicked.connect(self.validateForm)

        # If Cancel is pressed, terminate the program. The user can't
        # use it if he's not logged
        self.cancel_button.clicked.connect(self.closeEvent)


    def validateForm(self):

        """Slot to validate the infos. First, check them locally
        and then send them"""

        # http://sametmax.com/valider-une-adresse-email-avec-une-regex-en-python/

        validate = True

        email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
        re.IGNORECASE)

        if email_re.search(self.line_email.text()) is None:
            self.line_email.setStyleSheet('QLineEdit \
                                          {background-color: #FFA07A}')
            validate = False
        else:
            self.line_email.setStyleSheet(None)

        if self.combo_status.currentIndex() == 0:
            self.combo_status.setStyleSheet('QComboBox \
                                            {background-color: #FFA07A}')
            validate = False
        else:
            self.combo_status.setStyleSheet(None)

        if validate:
            payload = {'status': self.combo_status.currentIndex(),
                       'email': self.line_email.text(),
                       'user_input': self.line_captcha.text(),
                       'captcha_id': self.captcha_id,
                       'platform': platform.platform(),
                       }

            try:
                r = requests.post("http://chembrows.com/cgi-bin/sign.py",
                                  data=payload, timeout=20)
                # r = requests.post("http://127.0.0.1:8000/cgi-bin/sign.py",
                                  # data=payload)

            except (requests.exceptions.ReadTimeout,
                    requests.exceptions.Timeout):

                mes = """
                A time out error occured while contacting the server. \
                Please check you are connected to the internet, or contact us.
                """.replace('    ', '')

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

                self.logger.critical("ReadTimeout while signing up")
                return

            except requests.exceptions.ConnectionError:

                mes = """
                An error occured while contacting the server. Please check \
                you are connected to the internet, or contact us.
                """.replace('    ', '')

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

                self.logger.critical("ConnectionError while signing up")
                return

            except Exception as e:
                mes = """
                An unknown error occured while contacting the server. Please \
                check you are connected to the internet, or contact us. {}
                """.replace('    ', '').format(e)

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

                self.logger.critical("validateForm: {}".format(e),
                                       exc_info=True)
                return

            # Get the response from the server and log it
            self.logger.debug("Response from the server: {}".format(r.text))
            response = [part for part in r.text.split("\n") if part != '']

            # The server responded an user_id
            if 'user_id' in response[-1]:
                if not self.test:
                    self.parent.options.setValue('user_id',
                                                 response[-1].split(':')[-1])
                self.accept()
                self.validated = True

                # Delete the captcha file
                os.remove(os.path.join(self.DATA_PATH, "captcha.png"))

            # user_id already in db on the server
            elif response[-1] == 'A user with this email already exists':

                mes = """
                A user with the same email already exists. Please use another
                email.""".replace('    ', '')

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

                self.line_email.setStyleSheet('QLineEdit \
                                              {background-color: #FFA07A}')

            # The server says the captcha is incorrect
            elif response[-1] == 'Wrong captcha':

                mes = """
                The input for the captcha is incorrect. Please try again.
                """.replace('    ', '')

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

                self.line_captcha.setStyleSheet('QLineEdit \
                                                {background-color: #FFA07A}')

            # Unhandled response from the server
            else:
                mes = """
                Unknown error. Please retry and/or contact us.
                """.replace('    ', '')

                QtWidgets.QMessageBox.critical(self, "Signing up error", mes,
                                           QtWidgets.QMessageBox.Ok,
                                           defaultButton=QtWidgets.QMessageBox.Ok)


    def initUI(self):

        """Handles the display"""

        self.combo_status = QtWidgets.QComboBox()
        self.combo_status.addItem(None)
        self.combo_status.addItem("Student")
        self.combo_status.addItem("PhD student")
        self.combo_status.addItem("Post doc")
        self.combo_status.addItem("Researcher")
        self.combo_status.addItem("Professor")
        self.combo_status.addItem("Obi Wan Kenobi")

        self.form_sign = QtWidgets.QFormLayout()

        self.form_sign.addRow("Who are you? :", self.combo_status)

        # LineEdit for the email, with an icon opening an info box
        # info box about data privacy
        self.line_email = ButtonLineIcon(os.path.join(self.resource_dir,
                                                      'images/info'))
        self.line_email.buttonClicked.connect(self.showInfo)

        self.form_sign.addRow("Email :", self.line_email)

        # Label image for the captcha
        self.label_image = QtWidgets.QLabel()
        self.label_image.setAlignment(QtCore.Qt.AlignHCenter)

        self.form_sign.addRow(None, self.label_image)

        self.line_captcha = QtWidgets.QLineEdit()
        self.line_captcha.setPlaceholderText("I'm not a robot !")
        self.form_sign.addRow("Enter the captcha :", self.line_captcha)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)

        self.hbox_buttons = QtWidgets.QHBoxLayout()
        self.vbox_global = QtWidgets.QVBoxLayout()

        self.hbox_buttons.addWidget(self.cancel_button)
        self.hbox_buttons.addWidget(self.ok_button)

        self.vbox_global.addLayout(self.form_sign)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)
        self.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    obj = Signing()
    sys.exit(app.exec_())
