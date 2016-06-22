#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt4 import QtGui, QtCore
import webbrowser
import time
from functions import removeHtml

from twitter.api import Twitter
from twitter.oauth import OAuth, write_token_file, read_token_file

from log import MyLog
import constants


class MyTwit(QtGui.QDialog):

    """Module to authenticate the user on Twitter. Allows to tweet"""
    # http://www.adrianjock.com/twitter-myth-url-shorteners/
    # https://dev.twitter.com/faq#3
    # https://dev.twitter.com/rest/reference/get/help/configuration


    def __init__(self, parent, title, link, graphical=None):

        super(MyTwit, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.parent = parent

        # Remove html tags from the title
        self.title = removeHtml(title)

        self.link = link
        self.graphical = graphical

        self.DATA_PATH = self.parent.DATA_PATH

        # Get the logger of the parent window or create one
        self.l = getattr(parent, 'l', MyLog(self.DATA_PATH + "/activity.log"))

        self.CONSUMER_KEY = 'IaTVXKtZ7uBjzcVWzsVmMYKtP'
        self.CONSUMER_SECRET = '8hsz0Zj3CupFfvJMAhpG3UjMLs7HZjGywRsjRJI8IcjIA4NrEk'

        self.MY_TWITTER_CREDS = self.DATA_PATH + '/config/twitter_credentials'

        self.initUI()
        self.defineSlots()

        if not os.path.exists(self.MY_TWITTER_CREDS):
            self.openAuthPage()

        self.setTweetText()
        self.show()


    def openAuthPage(self):

        """Method to open the web page which gives the PIN code for
        authentication. When done, verify the pin code and write the
        keys into a local file. The user won't have to do the dance each
        time he wants to tweet"""

        twitter = Twitter(auth=OAuth('', '', self.CONSUMER_KEY, self.CONSUMER_SECRET), format='', api_version=None)

        token, token_secret = self.parseOauthTokens(twitter.oauth.request_token(oauth_callback="oob"))

        self.l.debug("Opening authentication URL")

        oauth_url = ('https://api.twitter.com/oauth/authorize?oauth_token=' + token)

        try:
            r = webbrowser.open(oauth_url)

            # Sometimes the last command can print some
            # crap. Wait a bit so it doesn't mess up the next
            # prompt.
            time.sleep(2)

            if not r:
                raise Exception()
        except Exception as e:
            QtGui.QMessageBox.critical(self, "Authentication", "ChemBrows could not open a web page.\nVisit oauth_url to get the PIN code",
                                       QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
            self.l.error("Authentication URL not opened")
            self.l.error("openAuthPage: {}".format(e), exc_info=True)


        pin = QtGui.QInputDialog.getText(self, "PIN verification", "Enter the PIN to authenticate yourself")

        oauth_verifier = pin[0]

        twitter = Twitter(auth=OAuth(token, token_secret, self.CONSUMER_KEY, self.CONSUMER_SECRET), format='', api_version=None)

        oauth_token, oauth_secret = self.parseOauthTokens(twitter.oauth.access_token(oauth_verifier=oauth_verifier))

        self.l.debug("Writing authentication file")
        write_token_file(self.MY_TWITTER_CREDS, oauth_token, oauth_secret)

        self.twitter = Twitter(auth=OAuth(oauth_token, oauth_secret,
                               self.CONSUMER_KEY, self.CONSUMER_SECRET))


    def parseOauthTokens(self, result):

        """Original function from the twitter.oauth_dance module.
        Don't really know what it does (probably parsing)..."""

        for r in result.split('&'):
            k, v = r.split('=')
            if k == 'oauth_token':
                oauth_token = v
            elif k == 'oauth_token_secret':
                oauth_token_secret = v
        return oauth_token, oauth_token_secret


    def setTweetText(self):

        """Method to shorten the title if it is too long"""

        # All links are 23 characters long, even the shorter ones
        len_data = 23

        # If graphical abstract included, shorten the title of 24 characters
        # https://dev.twitter.com/rest/reference/get/help/configuration
        try:
            if self.check_graphical.checkState() == 2:
                len_data += 24
        except AttributeError:
            pass

        LEN_TWEET = constants.LEN_TWEET

        # -1 for 1 space, -10 for #ChemBrows
        if len(self.title) >= LEN_TWEET - len_data - 1 - 10:
            title = self.title[:LEN_TWEET - len_data - 1 - 10 - 3].rstrip()
            title += "..."
        else:
            title = self.title + " "

        self.text_tweet.setText(title + self.link)


    def postTweet(self):

        """Simple method to post a tweet"""

        oauth_token, oauth_secret = read_token_file(self.MY_TWITTER_CREDS)

        try:
            if self.check_graphical.checkState() == 2:
                t_up = Twitter(domain='upload.twitter.com',
                               auth=OAuth(oauth_token, oauth_secret, self.CONSUMER_KEY, self.CONSUMER_SECRET))

                with open(self.DATA_PATH + "/graphical_abstracts/{}".format(self.graphical), "rb") as image:
                    imagedata = image.read()

                id_img = t_up.media.upload(media=imagedata)["media_id_string"]
            else:
                self.l.debug("No image, check box not checked")
                id_img = None

        except AttributeError:
            self.l.debug("No image, no check box at all")
            id_img = None

        twitter = Twitter(auth=OAuth(oauth_token, oauth_secret,
                                     self.CONSUMER_KEY, self.CONSUMER_SECRET))

        text = self.text_tweet.toPlainText() + " #ChemBrows"

        if id_img is None:
            try:
                twitter.statuses.update(status=text)
            except Exception as e:
                QtGui.QMessageBox.critical(self, "Twitter error", "ChemBrows could not tweet that.\nYour tweet is probably too long: {} chara.".format(len(text)),
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
                self.l.error('postTweet: {}'.format(e), exc_info=True)
        else:
            try:
                twitter.statuses.update(status=text, media_ids=id_img)
            except Exception as e:
                QtGui.QMessageBox.critical(self, "Twitter error", "ChemBrows could not tweet that.\nYour tweet is probably too long: {} chara.".format(len(text)),
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
                self.l.error("postTweet: {}".format(e), exc_info=True)

        self.close()


    def defineSlots(self):

        """Establish the slots"""

        # If next pressed, go to next slide
        self.ok_button.clicked.connect(self.postTweet)

        # Quit the tuto at any moment
        self.cancel_button.clicked.connect(self.done)


    def initUI(self):

        """Handles the display"""

        self.text_tweet = QtGui.QTextEdit()

        self.cancel_button = QtGui.QPushButton("Cancel", self)
        self.ok_button = QtGui.QPushButton("Tweet me !", self)

        self.hbox_buttons = QtGui.QHBoxLayout()
        self.vbox_global = QtGui.QVBoxLayout()

        # Display a check box to let the user choose
        # if he wants the graphical abstract to be displayed
        if self.graphical is not None:
            self.check_graphical = QtGui.QCheckBox("Include graphical abstract")
            self.check_graphical.setCheckState(2)
            self.check_graphical.stateChanged.connect(self.setTweetText)
            self.hbox_buttons.addWidget(self.check_graphical)

        self.hbox_buttons.addWidget(self.cancel_button)
        self.hbox_buttons.addWidget(self.ok_button)

        self.vbox_global.addWidget(self.text_tweet)
        self.vbox_global.addLayout(self.hbox_buttons)

        self.setLayout(self.vbox_global)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    parent = QtGui.QWidget()
    parent.DATA_PATH = '.'
    # obj = MyTwit(parent, "Mesoporous Ni<small><sub>60</sub></small>Fe<small><sub>30</sub></small>Mn<small><sub>10</sub></small>-alloy based metal/metal oxide composite thick films as highly active and robust oxygen evolution catalysts", "http://pubs.rsc.org/en/Content/ArticleLanding/2016/EE/C5EE02509E", "http pubs rsc org services images rscpubs eplatform service freecontent imageservice svc imageservice image ga id c5ee02509e")
    obj = MyTwit(parent, "<span class=\"hlFld-Title\">Molecular Rift: Virtual Reality for Drug Designers</span>", "http://dx.doi.org/10.1021/acs.jcim.5b00544", "http pubs acs org appl literatum publisher achs journals content jcisd8 0 jcisd8 ahead of print acs jcim 5b00544 20151111 images medium ci 2015 00544d_0015 gif")
    sys.exit(app.exec_())
