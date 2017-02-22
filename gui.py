#!/usr/bin/python
# coding: utf-8

import sys
import os
from PyQt5 import QtGui, QtSql, QtCore, QtWidgets
import datetime
import urllib
import fnmatch
import webbrowser
import requests
import platform
import validators
import collections as collec
import logging
import distutils.util

# Personal modules
from log import MyLog
from model import ModelPerso
from view import ViewPerso
from view_delegate import ViewDelegate
from worker import Worker
from predictor import Predictor
from settings import Settings
from advanced_search import AdvancedSearch
from tab import TabPerso
import functions
import hosts
from line_icon import ButtonLineIcon
from signing import Signing
from tuto import Tuto
from my_twit import MyTwit
from styles import MyStyles
from little_thread import LittleThread
from textbrowser import TextBrowserPerso

# To debug and profile. Comment for prod
# from memory_profiler import profile

# # DEBUG: do not show deprecation warningmport warningss
# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self):

        # Call processEvents regularly for the splash screen
        start_time = datetime.datetime.now()
        diff_time = start_time

        super(MyWindow, self).__init__()

        self.resource_dir, self.DATA_PATH = functions.getRightDirs()

        # Check if the running ChemBrows is a frozen app
        if getattr(sys, "frozen", False):
            # The program is NOT in debug mod if it's frozen
            self.debug_mod = False

            # http://stackoverflow.com/questions/10293808/how-to-get-the-path-of-the-executing-frozen-script
            # self.resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

            # Create the user directory if it doesn't exist
            os.makedirs(self.DATA_PATH, exist_ok=True)

            # Create the 'journals' directory, user side
            os.makedirs(os.path.join(self.DATA_PATH, 'journals/'),
                        exist_ok=True)

            # Create the logger w/ the appropriate size
            self.l = MyLog(os.path.join(self.DATA_PATH, "activity.log"))
            self.l.info("This version of ChemBrows is frozen")
            self.l.info("You are NOT in debug mode")
        else:
            # The program is in debug mod if it's not frozen
            self.debug_mod = True

            # Create the logger w/ the appropriate size
            self.l = MyLog(os.path.join(self.DATA_PATH, "activity.log"),
                           size=100000000)
            self.l.info("This version of ChemBrows is NOT frozen")
            self.l.info("You are in debug mod")

        # Set the logging level
        # self.l.setLevel(logging.INFO)
        self.l.setLevel(logging.DEBUG)

        self.l.info('Resources dir: {}'.format(self.resource_dir))
        self.l.info('Data dir: {}'.format(self.DATA_PATH))
        self.l.debug('Working dir: {}'.format(os.getcwd()))
        # self.l.setLevel(20)
        self.l.info(QtWidgets.QApplication.libraryPaths())
        self.l.info('Running {} {}'.format(platform.system(),
                                           platform.release()))
        self.l.info('Starting the program')

        QtWidgets.qApp.setWindowIcon(QtGui.QIcon(
            os.path.join(self.resource_dir, 'images', 'icon_main.png')))

        # Display a splash screen when booting
        # http://eli.thegreenplace.net/2009/05/09/creating-splash-screens-in-pyqt
        # CAREFUL, there is a bug with the splash screen
        # https://bugreports.qt.io/browse/QTBUG-24910
        splash_pix = QtGui.QPixmap(os.path.join(self.resource_dir, 'images',
                                                'splash.png'))
        self.splash = QtWidgets.QSplashScreen(splash_pix,
                                              QtCore.Qt.WindowStaysOnTopHint)
        self.splash.show()
        QtWidgets.qApp.processEvents()

        self.styles = MyStyles(QtWidgets.qApp)

        # Bool to check if the program is collecting data
        self.parsing = False

        # Bool to check if the ui is locked for the user
        self.blocking_ui = False

        QtWidgets.qApp.installEventFilter(self)

        # List to store the tags checked
        self.tags_selected = []

        # List to store all the views, models and proxies
        self.list_tables_in_tabs = []
        self.list_proxies_in_tabs = []


        # Object to store options and preferences
        self.options = QtCore.QSettings(os.path.join(self.DATA_PATH, 'config',
                                                     'options.ini'),
                                        QtCore.QSettings.IniFormat)

        # Look for updates
        QtWidgets.qApp.processEvents()
        self.upgrade()
        self.l.debug("bootCheckList took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        QtWidgets.qApp.processEvents()

        # Connect to the database & log the connection
        self.connectionBdd()
        self.defineActions()
        self.l.debug("connectionBdd & defineActions took {}"
                     .format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        QtWidgets.qApp.processEvents()
        self.correctionVersion()
        self.l.debug("correctionVersion took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Create the GUI
        QtWidgets.qApp.processEvents()
        self.initUI()
        self.l.debug("initUI took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Define the slots
        QtWidgets.qApp.processEvents()
        self.defineSlots()
        self.l.debug("defineSlots took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Creates the journals buttons
        QtWidgets.qApp.processEvents()
        self.displayTags()
        self.l.debug("displayTags took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Restore the settings
        QtWidgets.qApp.processEvents()
        self.restoreSettings()
        self.l.debug("restoreSettings took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        QtWidgets.qApp.processEvents()

        # Show the window
        self.show()
        self.splash.finish(self)
        self.l.debug("splash.finish() took {}".
                     format(datetime.datetime.now() - diff_time))

        self.l.info("Boot took {}".
                    format(datetime.datetime.now() - start_time))

        # Check if user_id present, and create some directories
        self.finishBoot()


    def justUpgraded(self):

        """Check if CB was just updated"""

        version_pkg = functions.getVersion()
        self.l.debug("Version pkg: {}".format(version_pkg))

        # If no whatsnew key in options.ini, display whatsnew.
        version = self.options.value("version", version_pkg, str)

        self.l.debug("Stored version: {}".format(version))

        self.options.setValue("version", version_pkg)

        if version < version_pkg:
            return True
        else:
            return False


    def availableUpgrade(self):

        """Check on the server if an upgrade is available"""

        local_ver = functions.getVersion()
        self.l.debug("Local version: {}".format(local_ver))

        try:
            r = requests.get("http://chembrows.com/downloads/version.txt")
        except Exception as e:
            self.l.error("availableUpgrade: {}".format(e), exc_info=True)
            return False

        os_name = distutils.util.get_platform()
        self.l.debug("OS name: {}".format(os_name))

        if os_name == 'win-amd64':
            platform = 'win'
        elif os_name == 'linux-x86_64':
            platform = 'nix'
        elif "macosx" and "x86_64" in os_name:
            platform = 'mac'
        else:
            self.l.error("availableUpgrade, unindentified platform")
            return False

        self.l.debug("Platform: {}".format(platform))

        for line in r.text.split("\n"):
            if platform in line:
                remote_ver = line.split(':')[1].strip()

        self.l.error("Remote version: {}".format(remote_ver))

        return local_ver < remote_ver


    def upgrade(self):

        """Performs some startup checks"""

        # Check if the running ChemBrows is a frozen app
        if self.debug_mod:
            return

        mes = """
        A new version of ChemBrows is available.<br/>
        You can download it from
        <a href='http://www.chembrows.com/website/index.php?static2/downloads'>
        www.chembrows.com</a>
        """.replace('    ', '')

        if self.availableUpgrade():

            QtWidgets.QMessageBox.information(self, "New version available",
                                              mes,
                                              QtWidgets.QMessageBox.Ok)

        if self.justUpgraded():

            with open(os.path.join(self.resource_dir,
                      'config/whatsnew.txt'), 'r', encoding='utf-8') as f:
                message = f.read()

            QtWidgets.QMessageBox.information(self, "What is new ?",
                                              message,
                                              QtWidgets.QMessageBox.Ok)


    def logConnection(self):

        """Originally, coded to perform check acces on the server. If
        the programm doesn't go commercial, RENAME THIS METHOD.
        For now, this method get the max id, used to know if incoming articles
        are new"""

        # Check if there is a user_id. If so, log the connection
        user_id = self.options.value("user_id", None)
        if user_id is None:
            return

        with open(os.path.join(self.resource_dir, 'config/version.txt'), 'r',
                  encoding='utf-8') as version_file:

            version = version_file.read()

        count_query = QtSql.QSqlQuery(self.bdd)

        count_query.exec_("SELECT COUNT(id) FROM papers")
        count_query.first()
        nbr_entries = count_query.record().value(0)
        self.l.info("Nbr of entries: {}".format(nbr_entries))

        payload = {'nbr_entries': nbr_entries,
                   'journals': self.getJournalsToParse(),
                   'user_id': user_id,
                   'version': version,
                   }

        try:
            if self.debug_mod:
                req = requests.post('http://chembrows.com/cgi-bin/log.py',
                                    params=payload, timeout=1)
            else:
                req = requests.post('http://chembrows.com/cgi-bin/log.py',
                                    params=payload, timeout=5)

            self.l.info('Server response: {}'.format(req.text))

        except Exception as e:
            self.l.error("logConnection: {}".format(e), exc_info=True)
            return

        if "user_id unregistered" in req.text:
            self.options.remove("user_id")
            self.l.error("The user_id was wrong. Set it to None")


    def correctionVersion(self):

        """Called during boot, to correct problems between versions"""

        # Get articles in ToRead list, old option
        ids_waited = self.options.value("ids_waited", [])

        if ids_waited:
            articles = {}

            query = QtSql.QSqlQuery(self.bdd)

            requete = "SELECT * FROM papers WHERE id IN ("

            # Building the query
            for each_id in ids_waited:
                if each_id != ids_waited[-1]:
                    requete = requete + str(each_id) + ", "
                else:
                    requete = requete + str(each_id) + ")"

            query.exec_(requete)

            while query.next():
                record = query.record()
                articles[record.value('id')] = record.value('new')

            searches_saved = QtCore.QSettings(os.path.join(self.DATA_PATH,
                                                           "config",
                                                           "searches.ini"),
                                              QtCore.QSettings.IniFormat)

            # Store the articles and their read states in a dictionary
            searches_saved.setValue("ToRead/articles", articles)

            self.options.remove('ids_waited')

        # Remove bool for dark background. Removed in version 0.9.9
        self.options.remove('Window/dark')


    def finishBoot(self):

        """Method to register a new user. When it is done,
        start the tutorial"""

        # Create the folder to store the graphical_abstracts if
        # it doesn't exist
        # http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
        os.makedirs(os.path.join(self.DATA_PATH, 'graphical_abstracts'),
                    exist_ok=True)


        # Check if there is a user_id. If not, register the user
        if self.options.value("user_id", None) is None:

            sign = Signing(self)

            # When the user is registered, start the tuto
            sign.accepted.connect(lambda: Tuto(self))


    def showAbout(self):

        """Shows a dialogBox w/ the version number"""

        version = functions.getVersion()

        mes = """
        You are using ChemBrows {}<br/><br/>
        Visit our web site: <a href='http://www.chembrows.com'>
        www.chembrows.com</a><br/><br/>
        To contact us: <a href="mailto:contact@chembrows.com">
        contact@chembrows.com</a><br/><br/>
        ChemBrows is released under the GNU GPL License.<br/><br/>
        DISCLAIMER: depending on the nature of the contracts between the
        professional institutions and the publishers, some users may not be
        allowed to automatically collect articles' metadata via their
        institution's Internet networks. ChemBrows' authors assume no liability
        for users' failures to comply with these contracts.
        """.replace('    ', '').format(version)

        # Use this complicated messageBox to get clickable URLs
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                'About ChemBrows', mes)
        box.setTextFormat(QtCore.Qt.RichText)
        box.setText(mes)
        box.exec()


    def connectionBdd(self):

        """Method to connect to the database. Creates it
        if it does not exist"""

        if not os.path.exists(os.path.join(self.DATA_PATH, "fichiers.sqlite")):
            self.l.info("db doesn't exist. Creating.")

        # Set the database
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName(os.path.join(self.DATA_PATH,
                                              "fichiers.sqlite"))

        self.bdd.open()

        query = QtSql.QSqlQuery(self.bdd)
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY\
                    AUTOINCREMENT, percentage_match REAL, doi TEXT, title\
                    TEXT, date TEXT, journal TEXT, authors TEXT, abstract\
                    TEXT, graphical_abstract TEXT, liked INTEGER, url TEXT,\
                    new INTEGER, topic_simple TEXT, author_simple TEXT)")

        if self.debug_mod:
            query.exec_("CREATE TABLE IF NOT EXISTS debug\
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, doi TEXT,\
                        title TEXT, journal TEXT, url TEXT)")

        # Create the model for the new tab
        self.model = ModelPerso(self)

        # Changes are not effective immediately, but it doesn't matter
        # because the view is updated each time a change is made
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)

        self.model.setTable("papers")
        self.model.select()

        count_query = QtSql.QSqlQuery(self.bdd)

        count_query.exec_("SELECT COUNT(id) FROM papers")
        count_query.first()
        nbr_entries = count_query.record().value(0)
        self.l.info("Nbr of entries: {}".format(nbr_entries))

        count_query.exec_("SELECT MAX(id) FROM papers")
        count_query.first()
        max_id_for_new = count_query.record().value(0)

        if type(max_id_for_new) is not int:
            max_id_for_new = 0

        self.l.info("Max id for new: {}".format(max_id_for_new))


    def getJournalsToParse(self):

        """Get the journals checked in the settings window"""

        # If no journals to parse in the settings,
        # parse them all. So build a journals_to_parse list
        # with all the journals
        journals = self.options.value("journals_to_parse", [])
        if not journals:
            journals = []
            for company in hosts.getCompanies():
                journals += hosts.getJournals(company)[1]

            self.options.remove("journals_to_parse")
            self.options.setValue("journals_to_parse", journals)

        return journals


    def parse(self):

        """Method to start parsing the data"""

        self.start_time = datetime.datetime.now()

        self.parsing = True
        self.blocking_ui = True

        # Disables the parse action to avoid double start
        self.parseAction.setEnabled(False)

        journals_to_parse = self.getJournalsToParse()

        # Create a dictionary w/ all the data concerning the journals
        # implemented in the program: names, abbreviations, urls.
        # Create a list of urls to parse data
        self.urls = []
        self.dict_journals = {}
        for company in hosts.getCompanies():
            data_company = hosts.getJournals(company)
            self.dict_journals[company] = data_company

            for abb, url in zip(data_company[1], data_company[2]):
                if abb in journals_to_parse:
                    self.urls.append(url)

        # Display a progress dialog box
        self.progress = QtWidgets.QProgressDialog("Collecting in progress",
                                                  "Cancel", 0, 100, self)
        self.progress.setWindowTitle("Collecting articles")
        self.progress.setModal(True)
        self.progress.canceled.connect(self.cancelRefresh)
        self.progress.show()

        self.urls_max = len(self.urls)

        # Get the optimal nbr of thread. Will vary depending
        # on the user's computer
        max_nbr_threads = QtCore.QThread.idealThreadCount()
        self.l.debug("IdealThreadCount: {}".format(max_nbr_threads))
        # max_nbr_threads = 1

        # Counter to count the new entries in the database
        self.counter_added = 0
        self.counter_updates = 0
        self.counter_rejected = 0
        self.counter_articles_failed = 0
        self.counter_images_failed = 0

        self.browsing_session = requests.session()

        # List of failed dl of RSS feeds
        self.list_failed_rss = []

        # List to store the threads.
        # The list is cleared when the method is started
        self.list_threads = []
        self.count_threads = 0
        for i in range(max_nbr_threads):
            try:
                url = self.urls[i]
                worker = Worker(self)
                worker.url_feed = url
                worker.finished.connect(self.checkThreads)
                self.urls.remove(url)
                self.list_threads.append(worker)
                worker.start()
                QtWidgets.qApp.processEvents()
            except IndexError:
                self.l.debug("parse, self.urls, IndexError")
                break


    # @profile
    def checkThreads(self):

        """Method to check the state of each thread.
        If all the threads are finished, enable the parse action.
        This slot is called when a thread is finished, to start the
        next one"""

        if not self.parsing:
            return

        elapsed_time = datetime.datetime.now() - self.start_time
        self.l.info(elapsed_time)

        self.count_threads += 1

        for worker in self.list_threads:
            if worker.isFinished():
                self.list_threads.remove(worker)
                del worker

        # Display the nbr of finished threads
        self.l.debug("Done: {}/{}".format(self.count_threads, self.urls_max))

        # # Display the progress of the parsing w/ the progress bar
        percent = self.count_threads * 100 / self.urls_max

        self.progress.setValue(round(percent, 0))
        if percent >= 100:
            self.progress.reset()
            QtWidgets.qApp.processEvents()

        if self.count_threads == self.urls_max:

            self.l.info("{} new entries added to the database".
                        format(self.counter_added))
            self.l.info("{} entries rejected".
                        format(self.counter_rejected))
            self.l.info("{} attempts to update entries\n".
                        format(self.counter_updates))

            self.l.info("{} RSS feeds were not downloaded:".
                        format(len(self.list_failed_rss)))
            for feed in self.list_failed_rss:
                self.l.debug(feed)
            self.l.debug("\n")

            self.l.info("{} articles failed".
                        format(self.counter_articles_failed))
            self.l.info("{} images failed".
                        format(self.counter_images_failed))

            total_time = datetime.datetime.now() - self.start_time
            self.l.debug("Total refresh time: {}".
                         format(total_time))

            # # TODO: checker cette instruction, should crash
            if self.counter_added > 0:
                self.l.debug("Time per paper: {} seconds".
                             format(total_time.seconds / (self.counter_added + self.counter_updates)))
            else:
                self.l.debug("Time per paper: irrelevant, 0 paper added")

            self.calculatePercentageMatch()

            self.parseAction.setEnabled(True)
            self.l.info("Parsing data finished. Enabling parseAction")

            # Update the view when a worker is finished
            self.searchByButton()
            self.updateCellSize()

            table = self.list_tables_in_tabs[self.onglets.currentIndex()]
            table.verticalScrollBar().setSliderPosition(0)
            table.selectionModel().clearSelection()

        else:
            if self.urls:
                self.l.debug("STARTING NEW THREAD")
                worker = Worker(self)
                worker.url_feed = self.urls[0]
                worker.finished.connect(self.checkThreads)
                self.urls.remove(worker.url_feed)
                self.list_threads.append(worker)
                worker.start()
                QtWidgets.qApp.processEvents()


    def cancelRefresh(self):

        """Slot to cancel the refresh process"""

        # Set the parsing bool to false, block checkThreads
        self.parsing = False

        # Cancel all the futures of each worker
        for worker in self.list_threads:
            for future in worker.list_futures:
                QtWidgets.qApp.processEvents()
                if type(future) is not bool:
                    future.cancel()
            self.l.debug("Killed all the futures for this worker")

        # Display a smooth progress bar
        self.progress = QtWidgets.QProgressDialog("Cancelling...", None, 0, 0, self)
        self.progress.setWindowTitle("Cancelling refresh")
        self.progress.show()

        while False in [worker.isFinished() for worker in self.list_threads]:
            QtWidgets.qApp.processEvents()

        self.progress.setLabelText("Loading notifications...")

        # Start loadNotifications in a thread (CPU consumming),
        # and display a smooth progressBar while in the function
        # But only if some articles were collected
        if self.counter_added > 0:
            worker = LittleThread(self.loadNotifications)
            worker.start()

            while worker.isRunning():
                QtWidgets.qApp.processEvents()
                worker.sleep(0.5)

        self.updateCellSize()
        self.progress.reset()

        self.parseAction.setEnabled(True)
        self.blocking_ui = False


    def defineActions(self):

        """On définit ici les actions du programme. Cette méthode est
        appelée à la création de la classe"""

        # Action to quit
        self.exitAction = QtWidgets.QAction('&Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Quit")
        self.exitAction.triggered.connect(self.closeEvent)

        # Action to refresh the posts
        self.parseAction = QtWidgets.QAction('&Refresh', self)
        self.parseAction.setShortcut('F5')
        self.parseAction.setToolTip("Refresh: download new posts")
        self.parseAction.triggered.connect(self.parse)

        # Action to calculate the percentages of match
        self.calculatePercentageMatchAction = QtWidgets.QAction('&Percentages', self)
        self.calculatePercentageMatchAction.setShortcut('F6')
        self.calculatePercentageMatchAction.setToolTip("Re-calculate Hot Paperness")
        self.calculatePercentageMatchAction.triggered.connect(lambda: self.calculatePercentageMatch(True))

        # Action to like a post
        self.toggleLikeAction = QtWidgets.QAction('Toggle like', self)
        self.toggleLikeAction.setShortcut('L')
        self.toggleLikeAction.triggered.connect(self.toggleLike)

        # Action to open the post in browser
        self.openInBrowserAction = QtWidgets.QAction('Open post in browser', self)
        self.openInBrowserAction.triggered.connect(self.openInBrowser)
        self.openInBrowserAction.setShortcut('Ctrl+W')

        # Action to show a settings window
        self.settingsAction = QtWidgets.QAction('Preferences', self)
        self.settingsAction.triggered.connect(lambda: Settings(self))

        self.tutoAction = QtWidgets.QAction('Tutorial', self)
        self.tutoAction.triggered.connect(lambda: Tuto(self))

        # Action to show a settings window
        self.showAboutAction = QtWidgets.QAction('About', self)
        self.showAboutAction.triggered.connect(self.showAbout)

        # # Action so show new articles
        # self.searchNewAction = QtWidgets.QAction('View unread', self)
        # self.searchNewAction.setToolTip("Display unread articles")
        # self.searchNewAction.triggered.connect(self.searchNew)

        # Action to toggle the read state of an article
        self.toggleReadAction = QtWidgets.QAction('Toggle read', self)
        self.toggleReadAction.setShortcut('M')
        self.toggleReadAction.triggered.connect(self.toggleRead)

        # Action to change the sorting method of the views. In the menu
        self.sortingPercentageAction = QtWidgets.QAction('By Hot Paperness', self, checkable=True)
        self.sortingPercentageAction.triggered.connect(lambda: self.changeSortingMethod(0))

        # Action to change the sorting method of the views. In the menu
        self.sortingDateAction = QtWidgets.QAction('By date', self, checkable=True)
        self.sortingDateAction.triggered.connect(lambda: self.changeSortingMethod(1))

        # Action to change the sorting method of the views, reverse the results. In the menu
        self.sortingReversedAction = QtWidgets.QAction('Reverse order', self, checkable=True)
        self.sortingReversedAction.triggered.connect(lambda: self.changeSortingMethod(self.sorting_method, True))

        # Action to change the sorting method of the views, reverse the results. In the menu
        self.emptyWaitAction = QtWidgets.QAction('Empty to-read list', self)
        self.emptyWaitAction.triggered.connect(self.emptyWait)

        # Action add/remove a post of the to-read list. For the right click
        self.toggleWaitAction = QtWidgets.QAction('Add/remove to to-read list', self)
        self.toggleWaitAction.triggered.connect(self.toggleWait)

        self.showLikesAction = QtWidgets.QAction('Show liked articles', self)
        self.showLikesAction.triggered.connect(self.showLikes)

        self.showReadAction = QtWidgets.QAction('Show read articles', self)
        self.showReadAction.triggered.connect(self.showRead)

        # Action to serve use as a separator
        self.separatorAction = QtWidgets.QAction(self)
        self.separatorAction.setSeparator(True)


    def changeSortingMethod(self, method_nbr, reverse=None):

        """
        Slot to change the sorting method of the
        articles. Get an int as a parameter:
        1 -> percentage match
        0 -> date
        reverse -> if True, descending order
        """

        if method_nbr is None:
            self.sorting_method = 1 - self.sorting_method
        else:
            # Set a class attribute, to save with the QSettings,
            # to restore the check at boot
            self.sorting_method = method_nbr

        if self.sorting_method == 1:
            self.sortingPercentageAction.setChecked(False)
            self.sortingDateAction.setChecked(True)
            self.button_sort_by.setText("Sort by Hot Paperness")
        elif self.sorting_method == 0:
            self.sortingPercentageAction.setChecked(True)
            self.sortingDateAction.setChecked(False)
            self.button_sort_by.setText("Sort by date")

        if reverse is not None:
            self.sorting_reversed = self.sortingReversedAction.isChecked()

        self.searchByButton()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


    def showLikes(self):

        """Show liked articles"""

        # Use the proxy to filter the column liked
        proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]
        proxy.setFilterRegExp(QtCore.QRegExp("[1]"))
        proxy.setFilterKeyColumn(9)

        # Get the maximum nbr of like articles
        count_like_max = QtSql.QSqlQuery(self.bdd)
        count_like_max.exec_("SELECT COUNT(id) FROM papers WHERE liked=1")
        count_like_max.first()
        nbr_likes = count_like_max.record().value(0)

        # Load all the liked articles:
        # Mandatory to avoid a bug: if there is no liked articles in the
        # chunk of the loaded sql entries, can cause a scrolling bug
        # We count the nbr_likes articles liked to try to optimize the
        # query
        while (proxy.canFetchMore(QtCore.QModelIndex()) and
               proxy.rowCount() < nbr_likes):

            proxy.fetchMore(QtCore.QModelIndex())

        self.updateCellSize()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


    def showRead(self):

        """
        Show read (new) articles
        new=1, which means unread
        This method works exactly like showLikes()
        """

        # Use the proxy to filter the column 'new'
        proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]
        proxy.setFilterRegExp(QtCore.QRegExp("[0]"))
        proxy.setFilterKeyColumn(11)

        # Get the maximum nbr of unread articles
        count_read_max = QtSql.QSqlQuery(self.bdd)
        count_read_max.exec_("SELECT COUNT(id) FROM papers WHERE new=0")
        count_read_max.first()
        nbr_read = count_read_max.record().value(0)

        while (proxy.canFetchMore(QtCore.QModelIndex()) and
               proxy.rowCount() < nbr_read):

            proxy.fetchMore(QtCore.QModelIndex())

        self.updateCellSize()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


    # @profile
    def closeEvent(self, event):

        """Method to perform actions before exiting.
        Allows to save the prefs in a file"""

        # http://stackoverflow.com/questions/9249500/
        # pyside-pyqt-detect-if-user-trying-to-close-window

        # Log connection
        self.logConnection()

        # Record the window state and appearance
        self.options.beginGroup("Window")

        # Reinitializing the keys
        self.options.remove("")

        self.l.debug("Saving windows state")
        self.options.setValue("window_geometry", self.saveGeometry())
        self.options.setValue("window_state", self.saveState())

        # Save the state of the window's splitter
        self.options.setValue("final_splitter", self.splitter2.saveState())

        # Save the sorting method
        self.options.setValue("sorting_method", self.sorting_method)
        self.options.setValue("sorting_reversed", self.sorting_reversed)

        # TODO
        # self.options.setValue("dark", self.dark)

        for index, each_table in enumerate(self.list_tables_in_tabs):
            self.options.setValue("header_state{0}".format(index),
                                  each_table.horizontalHeader().saveState())

        self.options.endGroup()

        searches_saved = QtCore.QSettings(os.path.join(self.DATA_PATH,
                                                       "config",
                                                       "searches.ini"),
                                          QtCore.QSettings.IniFormat)

        # Save the to-read list
        if self.waiting_list.articles:
            searches_saved.setValue("ToRead/articles",
                                    list(self.waiting_list.articles.keys()))
        else:
            searches_saved.remove("ToRead/articles")

        for index, each_table in enumerate(self.list_tables_in_tabs):
            tab_title = self.onglets.tabText(index)
            if tab_title != 'All articles':
                searches_saved.setValue("{}/articles".format(tab_title),
                                        each_table.articles)

        # Be sure ini files finished their tasks
        # Correct a bug
        self.options.sync()
        searches_saved.sync()

        self.model.submitAll()

        # Close the database connection
        self.bdd.removeDatabase(self.DATA_PATH + "/fichiers.sqlite")
        self.bdd.close()

        QtWidgets.qApp.quit()

        self.l.info("Closing the program")


    # @profile
    def loadNotifications(self, tab_number=None):

        """Method to find the number of unread articles,
        for each search. Load a list of id, for the unread articles,
        in each table. And a list of id, for the concerned articles, for
        each table. tab_number is here to load the notifications only for
        a particular tab, when loadNotifications is called after an update
        from an AdvancedSearch window"""

        self.l.debug("Starting loadNotifications")

        count_query = QtSql.QSqlQuery(self.bdd)
        count_query.setForwardOnly(True)

        # Don't treat the articles if it's the main tab, it's
        # useless because the article will be concerned for sure
        for table in self.list_tables_in_tabs[1:]:

            # If a particular tab is targeted, jump to it
            if tab_number is not None and self.list_tables_in_tabs.index(table) != tab_number:
                continue

            # Reset the articles dictionary, in any case
            table.articles = {}

            req_str = self.refineBaseQuery(table.base_query,
                                           table.topic_entries,
                                           table.author_entries,
                                           table.radio_states)
            count_query.exec_(req_str)

            id_bdd = count_query.record().indexOf('id')
            new = count_query.record().indexOf('new')

            while count_query.next():
                record = count_query.record()
                table.articles[record.value(id_bdd)] = record.value(new)

        # # Set the notifications for each tab
        for index in range(1, self.onglets.count()):
            table = self.onglets.widget(index)
            notifs = collec.Counter(table.articles.values())[1]
            self.onglets.setNotifications(index, notifs)

        self.l.debug("loadNotifications terminated")


    def restoreSettings(self):

        """Restore the prefs of the window"""

        searches_saved = QtCore.QSettings(self.DATA_PATH +
                                          "/config/searches.ini",
                                          QtCore.QSettings.IniFormat)

        # # Restore the to-read list
        self.createToRead(searches_saved)

        # Restore the saved searches
        for search_name in searches_saved.childGroups():

            # By pass the to-read list, already restored
            if search_name == "ToRead":
                continue

            query = searches_saved.value("{0}/sql_query".format(search_name))
            topic_entries = searches_saved.value("{0}/topic_entries".format(search_name), None)
            author_entries = searches_saved.value("{0}/author_entries".format(search_name), None)
            radio_states = searches_saved.value("{0}/radio_states".format(search_name), None)
            table = self.createSearchTab(search_name, query,
                                         topic_options=topic_entries,
                                         author_options=author_entries,
                                         radio_states=radio_states)
            table.articles = searches_saved.value("{0}/articles".format(search_name), {})

            tab_index = self.list_tables_in_tabs.index(table)

            notifs = collec.Counter(table.articles.values())[1]
            self.onglets.setNotifications(tab_index, notifs)

        # If windows settings are available, import and use them
        if "Window" in self.options.childGroups():

            self.restoreGeometry(self.options.value("Window/window_geometry"))
            self.restoreState(self.options.value("Window/window_state"))

            # for index, each_table in enumerate(self.list_tables_in_tabs):
                # header_state = self.options.value("Window/header_state{0}".format(index))
                # if header_state is not None:
                    # each_table.horizontalHeader().restoreState(self.options.value("Window/header_state{0}".format(index)))

            self.splitter2.restoreState(self.options.value("Window/final_splitter"))

            # # Bloc to restore the check of the sorting method, in the View menu
            # # of the menubar
            self.sorting_method = self.options.value("Window/sorting_method", 1, int)
            self.sorting_reversed = self.options.value("Window/sorting_reversed", False, bool)

            # Boolean: the background of the abstract zone is dark or not
            self.dark = self.options.value("Window/dark", False, bool)

            # Restore the journals selected (buttons pushed)
            self.tags_selected = self.options.value("Window/tags_selected", [])
            if self.tags_selected == self.getJournalsToParse():
                self.tags_selected = []
            if self.tags_selected:
                for button in self.list_buttons_tags:
                    if button.text() in self.tags_selected:
                        button.setChecked(True)
        else:
            # Create 2 attributes to store how the articles are sorted
            self.sorting_method = 0
            self.sorting_reversed = False
            self.dark = False

        self.changeSortingMethod(self.sorting_method, self.sorting_reversed)

        self.getJournalsToParse()

        # Timer to get the dimensions of the window right.
        # If the window is displayed too fast, I can't get the dimensions right
        QtCore.QTimer.singleShot(50, self.updateCellSize)


    def eventFilter(self, source, event) -> bool:

        """Sublclassing of this method allows to hide/show
        the journals filters on the left, through a mouse hover event.
        It also blocks the user interactions with the UI while parsing"""

        # do not hide menubar when menu shown
        if QtWidgets.qApp.activePopupWidget() is None:
            if event.type() == QtCore.QEvent.MouseMove:
                try:
                    if self.scroll_tags.isHidden():
                        try:
                            # Calculate the top zone where resizing can't
                            # happen (menubar, toolbar, etc)
                            table_y = self.toolbar.rect().height() + \
                                self.menubar.rect().height() + \
                                self.mapToGlobal(QtCore.QPoint(0, 0)).y() + \
                                self.hbox_central.getContentsMargins()[1]
                        except AttributeError:
                            pass
                        rect = self.geometry()
                        rect.setWidth(25)
                        rect.setTop(table_y)

                        if (rect.contains(event.globalPos()) and
                                not self.blocking_ui):
                            self.scroll_tags.show()
                    else:
                        width_layout = self.hbox_central.getContentsMargins()[2]
                        rect = QtCore.QRect(
                            self.scroll_tags.mapToGlobal(QtCore.QPoint(-width_layout, 0)),
                            self.scroll_tags.size())
                        if not rect.contains(event.globalPos()):
                            self.scroll_tags.hide()
                            # Give enough time to the program to get new splitter size,
                            # before resizing the cells
                            QtCore.QTimer.singleShot(20, self.updateCellSize)
                except AttributeError:
                    # self.l.debug("Event filter, AttributeError, probably starting the program")
                    pass

            elif event.type() == QtCore.QEvent.Leave and source is self:
                self.scroll_tags.hide()
                self.updateCellSize()

        return QtWidgets.QMainWindow.eventFilter(self, source, event)


    def resizeEvent(self, event):

        """Called when the Main window is resized.
        Reimplemented to resize the cell when the window
        is resized"""

        super(MyWindow, self).resizeEvent(event)

        QtCore.QTimer.singleShot(30, self.updateCellSize)


    def popup(self, pos):

        """Method to handle right-click"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        if not table.selectionModel().selection().indexes():
            return
        else:
            self.displayInfos()

        # Define a new postition for the menu
        new_pos = QtCore.QPoint(pos.x() + 10, pos.y() + 107)

        # Create the right-click menu and add the actions
        menu = QtWidgets.QMenu()
        menu.addAction(self.toggleLikeAction)
        menu.addAction(self.toggleReadAction)
        menu.addAction(self.openInBrowserAction)
        menu.addAction(self.toggleWaitAction)

        menu.exec_(self.mapToGlobal(new_pos))


    def defineSlots(self):

        """Connect the slots"""

        # Connect the back button
        # self.button_view_all.clicked.connect(self.resetView)

        # Launch the research if Enter pressed
        self.line_research.returnPressed.connect(self.research)
        self.line_research.buttonClicked.connect(self.clearSearch)

        # Perform some stuff when the tab is changed
        self.onglets.currentChanged.connect(self.tabChanged)

        # When the central splitter is moved, perform some actions,
        # like resizing the cells of the table
        self.splitter2.splitterMoved.connect(self.updateCellSize)

        # Share by email
        self.button_share_mail.clicked.connect(self.shareByEmail)

        # Share on Twitter
        self.button_twitter.clicked.connect(self.shareOnTwitter)

        # Button in the toolbar: parse
        self.button_refresh.clicked.connect(self.parse)

        # Button in the toolbar: calculate paperness
        self.button_calculate_percentage.clicked.connect(lambda: self.calculatePercentageMatch(True))

        # Button in the toolbar: advanced search
        self.button_advanced_search.clicked.connect(lambda: AdvancedSearch(self))

        self.button_zoom_more.clicked.connect(lambda: self.text_abstract.zoom(True))
        self.button_zoom_less.clicked.connect(lambda: self.text_abstract.zoom(False))

        self.button_search_new.clicked.connect(self.searchNew)

        self.button_settings.clicked.connect(lambda: Settings(self))


    def updateCellSize(self):

        """Update the cell size when the user moves the central splitter.
        For a better display"""

        # Get the size of the main splitter
        new_size = self.splitter2.sizes()[0]

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.resizeCells(new_size)
        table.updateHeight()


    def displayInfos(self):

        """Method to get the infos of a post. Also loads the graphical abstract.
        Basically build the infos displayed on the right side"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # If the user specifically clicks on the to read icon,
        # don't display infos, do nothing
        if table.toread_icon:
            return

        # Get the different infos for an article
        title = table.model().index(table.selectionModel().selection().indexes()[0].row(), 3).data()
        author = table.model().index(table.selectionModel().selection().indexes()[0].row(), 6).data()
        journal = table.model().index(table.selectionModel().selection().indexes()[0].row(), 5).data()
        date = table.model().index(table.selectionModel().selection().indexes()[0].row(), 4).data()

        doi = table.model().index(table.selectionModel().selection().indexes()[0].row(), 2).data()

        abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 7).data()

        try:
            # Checkings on the graphical abstract. Add the path of the picture
            # to the abstract if ok
            graphical_abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 8).data()

            if type(graphical_abstract) is str and graphical_abstract != "Empty":

                path = os.path.abspath(self.DATA_PATH +
                                       "/graphical_abstracts/" +
                                       graphical_abstract)

                # Get picture's width
                width = QtGui.QPixmap(path).width()

                # Set text_abstract initial width attribute
                self.text_abstract.ini_width = width

                # Get the path of the graphical abstract
                base = "<br/><br/><p align='center'><img width={} src='file:///{}' align='center' /></p>"

                base = base.format(width, path)
                abstract += base

        except TypeError:
            self.l.debug("No graphical abstract for this post, displayInfos()")

        # Reset text_abstract's zoom
        self.text_abstract.resetZoom()

        self.button_zoom_less.show()
        self.button_zoom_more.show()
        self.button_twitter.show()
        self.button_share_mail.show()

        self.label_date.setText(date)
        self.label_title.setText("<span style='font-size:{}pt; font-weight:bold'>{}</span>".format(self.styles.FONT_SIZE * 1.1, title))
        self.label_journal.setText(journal)

        if type(abstract) is str:
            self.text_abstract.setHtml(abstract)
        else:
            self.text_abstract.setHtml("")

        if type(author) is str:
            self.label_author.setText(author)
        else:
            self.label_author.setText("")

        # Some articles have an URL instead of a DOI (the publisher
        # does not provide the DOI in the abstract), so check and display
        # only the DOI
        if not validators.url(doi):
            self.label_doi.setText(doi)
        else:
            self.label_doi.setText("DOI unavailable")


    def tabChanged(self):

        """Slot to perform some actions when the current tab is changed.
        Mainly sets the tab query to the saved query"""

        # Submit the changes on the model.
        # Otherwise, a bug appears: one changing an article, the changes are
        # visible (trough the proxy) on all the articles at the same place
        # in all tabs
        self.model.submitAll()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        self.searchByButton()

        self.button_search_new.setText("View unread")
        for proxy in self.list_proxies_in_tabs:
            proxy.setFilterRegExp(QtCore.QRegExp('[01]'))
            proxy.setFilterKeyColumn(11)

        # Update the size of the columns of the view if the central
        # splitter moved
        self.updateCellSize()

        # Fix a display bug if toread list empty
        if not self.waiting_list.articles:
            table.initUI()


    def createToRead(self, searches_saved):

        """Method to restore the ToRead list.
        Might be useless, I think it could be done in restoreSettings()"""

        proxy = QtCore.QSortFilterProxyModel()

        # Don't "refresh" the proxy immediately, so when just unread articles
        # are shown, a click on an article doesn't make it disappear
        proxy.setDynamicSortFilter(False)

        proxy.setSourceModel(self.model)
        self.list_proxies_in_tabs.append(proxy)

        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.name_search = "ToRead"

        tableau.articles = searches_saved.value("ToRead/articles", {})

        requete = "SELECT * FROM papers WHERE id IN ("

        list_ids = list(tableau.articles.keys())

        # Building the query
        for each_id in list_ids:
            if each_id != list_ids[-1]:
                requete = requete + str(each_id) + ", "
            else:
                requete = requete + str(each_id) + ")"

        tableau.base_query = requete

        tableau.setModel(proxy)
        tableau.setItemDelegate(ViewDelegate(self))
        tableau.setSelectionBehavior(tableau.SelectRows)
        tableau.updateHeight()
        tableau.initUI()

        self.list_tables_in_tabs.append(tableau)

        notifs = collec.Counter(tableau.articles.values())[1]

        # Define an attribute for the to read list
        self.waiting_list = tableau

        self.onglets.addTab(tableau, "ToRead")
        self.onglets.setNotifications(1, notifs)


    def createSearchTab(self, name_search, query, topic_options=None,
                        author_options=None, radio_states=None, update=False):

        """Slot called from AdvancedSearch, when a new search is added,
        or a previous one updated"""

        # If the tab's query is updated from the advancedSearch window,
        # just update the base_query
        if update:
            self.model.submitAll()
            for index in range(self.onglets.count()):
                if name_search == self.onglets.tabText(index):
                    self.list_tables_in_tabs[index].base_query = query
                    self.list_tables_in_tabs[index].topic_entries = topic_options
                    self.list_tables_in_tabs[index].author_entries = author_options
                    self.list_tables_in_tabs[index].radio_states = radio_states
                    self.loadNotifications(index)
                    break

            if self.onglets.tabText(self.onglets.currentIndex()) == name_search:
                self.searchByButton()
            else:
                self.updateView()

            return

        proxy = QtCore.QSortFilterProxyModel()

        # Don't "refresh" the proxy immediately, so when just unread articles
        # are shown, a click on an article doesn't make it disappear
        proxy.setDynamicSortFilter(False)

        proxy.setSourceModel(self.model)
        self.list_proxies_in_tabs.append(proxy)

        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.name_search = name_search
        tableau.base_query = query
        tableau.topic_entries = topic_options
        tableau.author_entries = author_options
        tableau.radio_states = radio_states
        tableau.setModel(proxy)
        tableau.setItemDelegate(ViewDelegate(self))
        tableau.setSelectionBehavior(tableau.SelectRows)
        tableau.updateHeight()
        tableau.initUI()

        self.list_tables_in_tabs.append(tableau)

        self.onglets.addTab(tableau, name_search)

        return tableau


    def displayTags(self):

        """Slot to display push buttons on the left.
        One button per journal. Only display the journals
        selected in the settings window"""

        try:
            del self.list_buttons_tags
            self.clearLayout(self.vbox_all_tags)
        except AttributeError:
            pass

        self.list_buttons_tags = []

        journals_to_care = self.getJournalsToParse()

        if not journals_to_care:
            return

        journals_to_care.sort()

        for journal in journals_to_care:

            button = QtWidgets.QPushButton(journal)
            button.setAccessibleName("button_text_left")
            button.setCheckable(True)
            button.adjustSize()

            button.clicked[bool].connect(self.stateButtons)
            self.vbox_all_tags.addWidget(button)

            self.list_buttons_tags.append(button)

        self.vbox_all_tags.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_tags.setWidget(self.scrolling_tags)

        # Adjust the size of the left dock
        self.scrolling_tags.adjustSize()
        self.scroll_tags.setFixedWidth(self.scrolling_tags.size().width())


    def stateButtons(self, pressed):

        """Slot to check the journals push buttons"""

        if self.tags_selected == self.getJournalsToParse():
            self.tags_selected = []

        # Get the button pressed
        source = self.sender()

        # Build the list of ON buttons
        if source.parent() is self.scrolling_tags:
            if pressed:
                self.tags_selected.append(source.text())
            elif not pressed and len(self.tags_selected) > 0:
                self.tags_selected.remove(source.text())

        self.searchByButton()


    def searchByButton(self):

        """Slot to select articles by journal"""

        self.model.submitAll()

        # When last button is uncheck, select all the journals
        if not self.tags_selected:
            self.tags_selected = self.getJournalsToParse()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # Update the base query of the to-read list
        if table is self.waiting_list:
            requete = "SELECT * FROM papers WHERE id IN ("
            keys = list(table.articles.keys())
            for each_id in keys:
                if each_id != keys[-1]:
                    requete = requete + str(each_id) + ", "
                else:
                    requete = requete + str(each_id) + ")"
            table.base_query = requete

        self.query = QtSql.QSqlQuery(self.bdd)

        # The normal query:
        # SELECT * FROM papers WHERE topic_simple LIKE '% carboxyfluorescein %'
        # Becomes:
        # SELECT * FROM papers WHERE (topic_simple LIKE '% carboxyfluorescein %') AND journal IN ("ACS Catal."...

        refined_query = self.refineBaseQuery(table.base_query,
                                             table.topic_entries,
                                             table.author_entries,
                                             table.radio_states)

        if "WHERE" in refined_query:
            requete = refined_query.replace("WHERE ", "WHERE (")
            requete += ") AND journal IN ("
        else:
            requete = refined_query + " WHERE journal IN ("

        # Building the query
        for each_journal in self.tags_selected:
            if each_journal != self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            # Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(requete)
        self.query.exec_

        self.updateView()


    def searchNew(self):

        """Slot to show new articles. It's a toggable method, if
        the text of the sender button changes, the method does a different
        thing. It shows the new articles, or all depending of the
        button's state"""

        # If the button displays "View unread", shows the new articles
        # and change the button's text to "View all"
        if self.sender().text() == "View unread":
            self.button_search_new.setText("View all")
            proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]
            proxy.setFilterRegExp(QtCore.QRegExp("[1]"))
            proxy.setFilterKeyColumn(11)
            self.updateCellSize()

        # Else, do the contrary
        else:
            self.button_search_new.setText("View unread")
            proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]
            proxy.setFilterRegExp(QtCore.QRegExp("[01]"))
            proxy.setFilterKeyColumn(11)
            self.updateCellSize()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


    def refineBaseQuery(self, base_query, topic_options, author_options,
                        radio_states):

        """Method to refine the base_query of a view.
        A normal SQL query can't search a comma-separated list, so
        the results of the SQL query are filtered afterwords"""

        author_entries = author_options

        # If no * in the SQL query, return
        if (author_entries is None or
                not any('*' in element for element in author_entries)):

            return base_query

        query = QtSql.QSqlQuery(self.bdd)
        query.prepare(base_query)
        query.exec_()

        # Prepare a list to store the filtered items
        list_ids = []

        while query.next():
            record = query.record()

            # Normalize the authors string of the items
            authors = record.value('authors').split(', ')
            authors = [element.lower() for element in authors]

            adding = True
            list_adding_or = []

            # Loop over the 3 kinds of condition: AND, OR, NOT
            for index, entries in enumerate(author_entries):
                if not entries:
                    continue

                # For each person in the SQL query
                for person in entries.split(','):

                    # Normalize the person's string
                    person = person.strip().lower()

                    # AND condition
                    if index == 0 and not radio_states[0]:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if not matching:
                                adding = False
                                break

                    # OR condition
                    elif index == 0 and radio_states[0]:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                list_adding_or.append(True)
                                continue
                            else:
                                list_adding_or.append(False)
                        else:
                            # Tips for any()
                            # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
                            # if any(person in element for element in authors):
                            if person in authors:
                                list_adding_or.append(True)
                                continue
                            else:
                                list_adding_or.append(False)

                    # NOT condition
                    if index == 1:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                adding = False
                                break
                        else:
                            # if any(person in element for element in authors):
                            if person in authors:
                                adding = False
                                break

                if list_adding_or and True not in list_adding_or:
                    adding = False
                if not adding:
                    break

            if adding:
                list_ids.append(record.value('id'))

        if not list_ids:
            requete = "SELECT * FROM papers WHERE id IN ()"

            return requete
        else:
            requete = "SELECT * FROM papers WHERE id IN ("

            # Building the query
            for each_id in list_ids:
                if each_id != list_ids[-1]:
                    requete = requete + str(each_id) + ", "
                # Close the query if last
                else:
                    requete = requete + str(each_id) + ")"

            return requete


    def research(self):

        """Slot to search on title and abstract.
        The search can be performed on a particular tab"""

        self.model.submitAll()

        # If it's not the main tab, filter through the already-filtered
        # results of a particular tab
        if self.onglets.currentIndex() != 0:
            table = self.list_tables_in_tabs[self.onglets.currentIndex()]
            requete = self.refineBaseQuery(
                table.base_query, table.topic_entries,
                table.author_entries, table.radio_states)
            requete = requete.replace("WHERE ", "WHERE (")
            requete += ") AND (topic_simple LIKE '%{}%' OR author_simple LIKE \
                       '%{}%') AND journal IN ("
        else:
            requete = "SELECT * FROM papers WHERE (topic_simple LIKE '%{}%' \
                      OR author_simple LIKE '%{}%') AND journal IN ("

        results = functions.simpleChar(self.line_research.text())

        self.query = QtSql.QSqlQuery(self.bdd)

        # Search only the selected journals
        for each_journal in self.tags_selected:
            if each_journal != self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"


        self.query.prepare(requete.format(results, results))
        self.query.exec_()

        self.updateView()


    def clearSearch(self):

        """Method to clear the research bar"""

        self.line_research.clear()
        self.line_research.returnPressed.emit()
        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


    def clearLayout(self, layout):

        """Method to erase the widgets from a layout"""

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                    QtWidgets.qApp.processEvents()
                else:
                    self.clearLayout(item.layout())


    def resetView(self):

        """Slot to reset view, clean the graphical abstract, etc"""

        proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]

        # Cleaning title, authors and abstract
        self.label_author.setText("")
        self.label_title.setText("")
        self.label_journal.setText("")
        self.label_date.setText("")
        self.label_doi.setText("")
        self.text_abstract.setHtml("")

        # Uncheck the journals buttons on the left
        for button in self.list_buttons_tags:
            button.setChecked(False)

        for proxy in self.list_proxies_in_tabs:
            proxy.setFilterRegExp(QtCore.QRegExp('[01]'))
            proxy.setFilterKeyColumn(11)

        self.tags_selected = self.getJournalsToParse()
        self.searchByButton()

        # Clear the search bar
        self.line_research.clear()

        self.button_zoom_less.hide()
        self.button_zoom_more.hide()
        self.button_twitter.hide()
        self.button_share_mail.hide()

        # Put the vertical scroll bar at the top
        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.verticalScrollBar().setSliderPosition(0)
        table.selectionModel().clearSelection()


        # Delete last query
        try:
            del self.query
        except AttributeError:
            self.l.warn("Pas de requête précédente")

        # Update the cells of the view, resize them
        self.updateCellSize()


    def updateNotifications(self, id_bdd, remove=True):

        """Slot to update the number of unread articles,
        in each tab. Called by markOneRead, toggleRead and toggleWait"""

        for index in range(1, self.onglets.count()):

            # remove the id of the list of the new articles
            if id_bdd in self.onglets.widget(index).articles and remove:
                self.onglets.widget(index).articles[id_bdd] = 0

            # Add the id to the list of new articles
            elif id_bdd in self.onglets.widget(index).articles and not remove:
                self.onglets.widget(index).articles[id_bdd] = 1

            table = self.onglets.widget(index)
            notifs = collec.Counter(table.articles.values())[1]
            self.onglets.setNotifications(index, notifs)


    def markOneRead(self, element):

        """Slot to mark an article read"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        id_bdd = table.model().index(element.row(), 0).data()
        new = table.model().index(element.row(), 11).data()

        # update_new: to check if the user is currently clicking
        # on the read icon. If so, don't mark the article as read
        if new == 0 or table.toread_icon is True:
            return
        else:

            # Save the current line
            line = table.selectionModel().currentIndex().row()

            # Change the data in the model
            table.model().setData(table.model().index(line, 11), 0)

            index = table.model().index(line, 11)

            table.model().dataChanged.emit(index, index)

            table.selectRow(line)

            self.updateNotifications(id_bdd)


    def toggleWait(self):

        """Method to add/remove an article in the To-read list"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        line = table.selectionModel().currentIndex().row()
        id_bdd = table.model().index(line, 0).data()
        new = table.model().index(line, 11).data()
        waited = id_bdd in self.waiting_list.articles

        # Check if the to read list is empty
        empty = self.waiting_list.articles == {}

        if waited:
            del self.waiting_list.articles[id_bdd]

            # Immediately visually remove the post from the to read list
            # if the to read list is displayed
            if table is self.waiting_list:

                # Submit changes to the model, the viewport is about to change
                # self.model.submitAll()
                self.searchByButton()

                # Update the cells bc the scroll bar can disappear when
                # posts are removed from the to read list
                self.updateCellSize()

            self.updateNotifications(id_bdd)
        else:
            if new:
                self.waiting_list.articles[id_bdd] = 1
            else:
                self.waiting_list.articles[id_bdd] = 0

        # Update the notifications of the to-read list
        notifs = collec.Counter(self.waiting_list.articles.values())[1]
        self.onglets.setNotifications(1, notifs)

        # If the to read list was empty and is not anymore, fix the
        # header of the to read list
        if empty and len(self.waiting_list.articles) == 1:
            self.waiting_list.initUI()


    def emptyWait(self):

        """Method to empty the to-read list"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        self.waiting_list.articles = {}

        # Update the notifications of the to-read list
        index = self.list_tables_in_tabs.index(self.waiting_list)
        self.onglets.setNotifications(index, 0)

        if table is self.waiting_list:
            self.searchByButton()
            self.updateCellSize()


    def updateView(self):

        """Method to update the view after a model change.
        If an item was selected, the item is re-selected"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        proxy = self.list_proxies_in_tabs[self.onglets.currentIndex()]

        try:
            # Try to update the model
            self.model.setQuery(self.query)
            proxy.setSourceModel(self.model)
            table.setModel(proxy)
        # self.query doesn't exist
        except AttributeError:
            self.l.debug("updateView, AttributeError")
            self.model.setQuery(self.refineBaseQuery(table.base_query,
                                                     table.topic_entries,
                                                     table.author_entries,
                                                     table.radio_states))
            proxy.setSourceModel(self.model)
            table.setModel(proxy)


    def toggleRead(self):

        """Method to invert the value of new.
        So, toggle the read/unread state of an article"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        id_bdd = table.model().index(table.selectionModel().currentIndex().row(), 0).data()
        new = table.model().index(table.selectionModel().currentIndex().row(), 11).data()
        line = table.selectionModel().currentIndex().row()

        # Invert the value of new
        new = 1 - new

        index = table.model().index(line, 11)

        table.model().setData(index, new)
        table.model().dataChanged.emit(index, index)

        if new == 0:
            self.updateNotifications(id_bdd)
        else:

            # Check if the article is like. If it is, unlike it. An article
            # can't be unread and liked
            like = table.model().index(table.selectionModel().currentIndex().row(), 9).data()
            if like == 1:
                index = table.model().index(line, 9)
                table.model().setData(index, 0)
                table.model().dataChanged.emit(index, index)
            self.updateNotifications(id_bdd, remove=False)

        table.viewport().update()
        table.selectRow(line)


    def resetDb(self):

        """Method to reset the db. Will set the 'new' field of every entry
        to 1, and the liked field to 0"""

        mes = """
        You are about to reset your database. All the articles will be marked
         as new, and all liked articles will be unliked. Use this feature if
         you want to start fresh without loosing collected articles. If you
         click OK, the process will start.
        """

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")
        mes = mes.replace("\n", "")

        choice = QtWidgets.QMessageBox.critical(self, "Resetting database", mes,
                                            QtWidgets.QMessageBox.Cancel |
                                            QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Cancel:
            return

        progress = QtWidgets.QProgressDialog("Resetting database...",
                                         None, 0, 0, self)
        progress.setWindowTitle("resetting database")
        progress.show()
        QtWidgets.qApp.processEvents()

        # Perform the db modifications in a thread
        def internalReset():

            """Internal function, will be executed in a thread"""

            query = QtSql.QSqlQuery(self.bdd)
            query.exec_("UPDATE papers SET liked=0, new=1, percentage_match=0")
            self.l.info("Reset db")

            self.loadNotifications()
            self.searchByButton()
            self.updateCellSize()

        worker = LittleThread(internalReset)
        worker.start()

        while worker.isRunning():
            QtWidgets.qApp.processEvents()
            worker.sleep(0.5)

        progress.reset()
        self.l.info("resetDb completed")


    def eraseDb(self):

        """Method to completely erase the database. Will also vacuum it"""

        mes = """
        You are about to completely erase your database. ALL the data regarding
         articles will be lost. If you click OK, the process will start.
        """

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")
        mes = mes.replace("\n", "")

        choice = QtWidgets.QMessageBox.critical(self, "Erasing database", mes,
                                            QtWidgets.QMessageBox.Cancel |
                                            QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Cancel:
            return

        progress = QtWidgets.QProgressDialog("Erasing database...",
                                         None, 0, 0, self)
        progress.setWindowTitle("Erasing database")
        progress.show()
        QtWidgets.qApp.processEvents()

        def internalErase():

            """Internal function, will be executed in a thread"""

            query = QtSql.QSqlQuery(self.bdd)
            query.exec_("DELETE FROM papers")
            self.l.info("All articles deleted")

            self.bdd.close()
            self.bdd.open()
            query = QtSql.QSqlQuery(self.bdd)

            # Vacuum the db. Removes free space from db
            query.prepare("VACUUM papers")
            query.exec_()
            self.l.info("Data base vacuumed")

            self.loadNotifications()

            self.searchByButton()
            self.updateCellSize()

        worker = LittleThread(internalErase)
        worker.start()

        while worker.isRunning():
            QtWidgets.qApp.processEvents()
            worker.sleep(0.5)

        progress.reset()
        self.l.info("eraseDb completed")


    def cleanDb(self):

        """
        Slot to clean the database. Called from the window settings, but
        better to be here. Deletes the orphan pictures in the
        graphical_abstracts folder. Clean misformatted fields. Deletes
        incomplete articles.
        """

        mes = """
        You are about to clean your database, and you might loose data.
        The process will erase articles from unselected journals.
        The process will erase orphan graphical abstracts.
        The process will erase incomplete articles.
        The process will clean misformatted fields in your database.
        It might be a good idea to use this feature after an update.
        If you click OK, the cleaning process will start
        """

        # Clean the tabs in the message (tabs are 4 spaces)
        mes = mes.replace("    ", "")

        choice = QtWidgets.QMessageBox.critical(self, "Cleaning database", mes,
                                            QtWidgets.QMessageBox.Cancel |
                                            QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Cancel:
            return

        # Display a progress bar
        progress = QtWidgets.QProgressDialog("Deleting articles from unfollowed journals", None, 0, 100, self)
        progress.setWindowTitle("Cleaning database")
        progress.show()
        QtWidgets.qApp.processEvents()

        # Create a query and start a transaction, more efficient
        query = QtSql.QSqlQuery(self.bdd)
        self.bdd.transaction()

        # Clean authors field for misformatting
        query.exec_("UPDATE papers SET authors=replace(authors, '  ', ' ' ) WHERE \
                     authors LIKE '%  %'")
        query.exec_("UPDATE papers SET authors=replace(authors, ' ,', ',' ) WHERE \
                     authors LIKE '%  %'")
        query.exec_("UPDATE papers SET author_simple=replace(author_simple, '  ', \
                     ' ' ) WHERE author_simple LIKE '%  %'")

        # Delete all the articles of unselected journals
        requete = "DELETE FROM papers WHERE journal NOT IN ("
        journals_to_care = self.getJournalsToParse()

        # Building the query
        for each_journal in self.getJournalsToParse():
            if each_journal != journals_to_care[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            # Close the query if last
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        query.prepare(requete)
        query.exec_()

        self.l.error(self.bdd.lastError().text())

        self.l.info("Removed unintersting journals from the database")

        progress.setLabelText("Deleting articles with empty abstracts")
        progress.setValue(20)
        QtWidgets.qApp.processEvents()

        query.exec_("DELETE FROM papers WHERE abstract=''")

        if not self.bdd.commit():
            self.l.critical("Problem while commiting, cleanDb")
        else:
            self.l.info("Removed incomplete articles from the database")

        progress.setLabelText("Deleting useless images")
        progress.setValue(40)
        QtWidgets.qApp.processEvents()

        query.exec_("SELECT graphical_abstract FROM papers WHERE graphical_abstract != 'Empty'")

        images_path = []
        while query.next():
            images_path.append(query.record().value('graphical_abstract'))

        list_pics = os.listdir(self.DATA_PATH + "/graphical_abstracts/")

        pics_to_remove = list(set(list_pics) - set(images_path))

        self.l.debug("{} images to remove".format(len(pics_to_remove)))

        for pic in pics_to_remove:
            os.remove(os.path.abspath(self.DATA_PATH +
                "/graphical_abstracts/{0}".format(pic)))
            self.l.debug("removing {}".format(pic))

        self.l.debug("Deleted all the useless images")

        progress.setLabelText("Building list of filtered articles")
        progress.setValue(60)
        QtWidgets.qApp.processEvents()

        query.exec_("SELECT id, doi, title, journal, url FROM papers")

        # Build a list of tuples w/ all the rejected articles
        articles_to_reject = []
        while query.next():
            record = query.record()
            reject = hosts.reject(record.value('title'))

            if reject:
                id = record.value('id')
                doi = record.value('doi')
                title = record.value('title')
                journal = record.value('journal')
                url = record.value('url')

                # Tuple representing an article
                articles_to_reject.append((id, doi, title, journal, url))

        self.l.info("{} entries rejected will be deleted".
                    format(len(articles_to_reject)))

        progress.setLabelText("Deleting filtered articles")
        progress.setValue(80)
        QtWidgets.qApp.processEvents()

        requete = "DELETE FROM papers WHERE id IN ("

        # Building the query
        for article in articles_to_reject:
            if article != articles_to_reject[-1]:
                requete = requete + str(article[0]) + ", "
            # Close the query if last
            else:
                requete = requete + str(article[0]) + ")"

        query.exec_(requete)

        self.l.info("Rejected entries deleted from the database")

        QtWidgets.qApp.processEvents()

        if self.debug_mod:
            progress.setLabelText("Building list of filtered articles")
            progress.setValue(85)
            QtWidgets.qApp.processEvents()

            # Build a list of DOIs to avoid duplicate in debug table
            list_doi = []
            query.exec_("SELECT doi FROM debug")
            while query.next():
                list_doi.append(query.record().value('doi'))

            progress.setLabelText("Inserting filtered articles in debug db")
            progress.setValue(90)
            QtWidgets.qApp.processEvents()

            # Insert all the rejected articles in the debug table
            self.bdd.transaction()
            query.prepare("INSERT INTO debug (doi, title, journal, url) VALUES(?, ?, ?, ?)")

            for article in articles_to_reject:
                if article[1] not in list_doi:
                    for value in article[1:]:
                        query.addBindValue(value)
                    query.exec_()

            if not self.bdd.commit():
                self.l.critical("Problem while inserting rejected articles, cleanDb")
            else:
                self.l.info("Inserting rejected articles into the database")

        self.bdd.close()
        self.bdd.open()
        query = QtSql.QSqlQuery(self.bdd)

        # Vacuum the db. Removes free space from db
        query.prepare("VACUUM papers")
        query.exec_()
        self.l.info("Data base vacuumed")

        progress.setLabelText("Loading notifications")
        progress.setValue(95)
        QtWidgets.qApp.processEvents()

        self.loadNotifications()

        progress.setValue(100)
        QtWidgets.qApp.processEvents()
        progress.reset()

        self.searchByButton()
        self.updateCellSize()


    def openInBrowser(self):

        """Slot to open the post in browser
        http://stackoverflow.com/questions/4216985/call-to-operating-system-to-open-url
        """

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        try:
            url = table.model().index(table.selectionModel().selection().indexes()[0].row(), 10).data()
        except IndexError:
            self.l.debug("No url to open. openInBrowser")

        if not url:
            return
        else:
            webbrowser.open(url, new=0, autoraise=True)
            self.l.info("Opening {0} in browser".format(url))


    def shareOnTwitter(self):

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # Check if something is selected
        if not table.selectionModel().selection().indexes():
            return

        self.l.info("Sharing on Twitter")

        # Get the infos
        title = table.model().index(table.selectionModel().selection().indexes()[0].row(), 3).data()
        link = table.model().index(table.selectionModel().selection().indexes()[0].row(), 10).data()
        graphical_abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 8).data()

        if type(graphical_abstract) is str and graphical_abstract != "Empty":
            MyTwit(title, link, graphical_abstract, self)
        else:
            MyTwit(title, link, self)


    def shareByEmail(self):

        """
        Method to send an article via email. The methods fills all the fields, except
        the recepient(s). It sends the title, the authors, the journals, the abstract,
        and provides a link to the editor's website. Also promotes chemBrows by inserting
        its name in the title and at the end of the body.
        http://www.2ality.com/2009/02/generate-emails-with-mailto-urls-and.html
        """

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # Check if something is selected
        if not table.selectionModel().selection().indexes():
            return

        self.l.info("Sending by email")

        # Get the infos
        title = table.model().index(table.selectionModel().selection().indexes()[0].row(), 3).data()
        link = table.model().index(table.selectionModel().selection().indexes()[0].row(), 10).data()

        # Create a simple title, by removing html tags (tags are not accepted in a mail subject)
        simple_title = functions.removeHtml(title) + " : spotted by ChemBrows"

        body = "Click on this link to see the article on the editor's website: {}\n\nThis article was spotted by ChemBrows: www.chembrows.com"
        body = body.format(link)

        url = "mailto:?subject={}&body={}"

        # if sys.platform=='win32':
        if sys.platform in ['win32', 'cygwin', 'win64']:
            body = urllib.parse.quote(body)
            url = url.format(simple_title, body)
            webbrowser.open(url)

        elif sys.platform == 'darwin':
            url = url.format(simple_title, body)
            webbrowser.open(url)
        else:
            # Create an url to be opened with a mail client
            body = urllib.parse.quote(body)
            url = url.format(simple_title, body)
            webbrowser.open(url)


    def calculatePercentageMatch(self, alone=False):

        """Slot to calculate the match percentage.
        alone=True means the user started the calculations only"""

        # Block user input. This bool could be True if parse() was started,
        # but it could also be False if the user refreshes the paperness
        self.blocking_ui = True

        self.model.submitAll()

        self.predictor = Predictor(self.l,
                                   list(self.waiting_list.articles.keys()),
                                   self.bdd)

        def whenDone():

            """Internal function called when the thread for percentages
            calculations is finished"""

            self.searchByButton()

            # If parsing, load the notifications
            # load the notifications only if some articles were collected
            try:
                if self.counter_added > 0:
                    self.progress.setWindowTitle("Loading notifications")
                    self.progress.setLabelText("Loading notifications...")
                    worker = LittleThread(self.loadNotifications)
                    worker.start()

                    while worker.isRunning():
                        QtWidgets.qApp.processEvents()
                        worker.sleep(0.5)

            except AttributeError:
                self.l.debug("No entries added, skipping loadNotifications")

            # Unlock the UI by setting this to False
            self.blocking_ui = False

            mes = "ChemBrows does not have enough data to calculate the Hot paperness yet.\n\n"
            mes += "Feed it more !"

            self.progress.reset()

            # Display a message if the classifier is not trained yet
            if not self.predictor.initiated or not self.predictor.calculated_something:

                QtWidgets.QMessageBox.information(self, "Feed ChemBrows", mes,
                                                  QtWidgets.QMessageBox.Ok)
                QtWidgets.qApp.processEvents()

            if not alone:
                # Display the number of articles added
                mes = "{} new articles were added to your database !"
                mes = mes.format(self.counter_added)
                QtWidgets.QMessageBox.information(self, "New articles", mes,
                                              QtWidgets.QMessageBox.Ok)

            del self.predictor


        # https://contingencycoder.wordpress.com/2013/08/04/quick-tip-qprogressbar-as-a-busy-indicator/
        # If the range is set to 0, get a busy progress bar,
        # without percentage
        self.progress = QtWidgets.QProgressDialog("Calculating Hot Paperness...",
                                              None, 0, 0, self)
        self.progress.setWindowTitle("Hot Paperness calculation")
        self.progress.setModal(True)
        self.progress.show()

        self.predictor.initializePipeline()
        self.predictor.finished.connect(whenDone)
        self.predictor.start()

        # While calculating, display a smooth progress bar
        try:
            while not self.predictor.isFinished():
                QtWidgets.qApp.processEvents()
                self.predictor.sleep(0.5)
        except AttributeError:
            self.l.debug("Predictor deleted while processEvents ?")
            pass


    def toggleLike(self):

        """Slot to mark a post liked"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        like = table.model().index(
            table.selectionModel().currentIndex().row(), 9).data()
        line = table.selectionModel().currentIndex().row()

        # Invert the value of new
        if type(like) is int:
            like = 1 - like
        else:
            like = 1

        index = table.model().index(line, 9)
        table.model().setData(index, like)

        table.model().dataChanged.emit(index, index)
        table.viewport().update()

        table.selectRow(line)


    def initUI(self):

        """Build the program's interface"""

        self.setWindowTitle('ChemBrows')

        font = QtGui.QFont()
        font.setStyleHint(QtGui.QFont.System)
        font.setPointSize(self.styles.FONT_SIZE)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        QtWidgets.qApp.setFont(font)

        self.l.debug('Font: {}'.format(font.family()))
        self.l.debug('Font size: {}pt'.format(self.styles.FONT_SIZE))

        # ------------------------- BUILDING THE MENUS -------------------------------------------------------------

        self.menubar = self.menuBar()

        # Building files menu
        self.fileMenu = self.menubar.addMenu('&Files')
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addAction(self.exitAction)

        # Building tools menu
        self.toolMenu = self.menubar.addMenu("&Tools")
        self.toolMenu.addAction(self.parseAction)
        self.toolMenu.addAction(self.calculatePercentageMatchAction)
        self.toolMenu.addAction(self.toggleReadAction)
        self.toolMenu.addAction(self.toggleLikeAction)
        self.toolMenu.addAction(self.openInBrowserAction)
        self.toolMenu.addAction(self.toggleWaitAction)
        self.toolMenu.addAction(self.emptyWaitAction)

        self.viewMenu = self.menubar.addMenu("&View")
        self.sortMenu = self.viewMenu.addMenu("Sorting")
        self.sortMenu.addAction(self.sortingPercentageAction)
        self.sortMenu.addAction(self.sortingDateAction)
        self.sortMenu.addAction(self.separatorAction)
        self.sortMenu.addAction(self.sortingReversedAction)
        self.viewMenu.addAction(self.showLikesAction)
        self.viewMenu.addAction(self.showReadAction)

        self.helpMenu = self.menubar.addMenu("&Help")
        self.helpMenu.addAction(self.tutoAction)
        self.helpMenu.addAction(self.showAboutAction)

        # # ------------------------- TOOLBAR  -----------------------------------------------

        # Add a toolbar and name it to identiy it
        # Then add the widgets
        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.setMovable(False)

        # Refresh button. I use buttons and not actions because I want to
        # set their style
        self.button_refresh = QtWidgets.QPushButton()
        self.button_refresh.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, "images/refresh.png")))
        self.button_refresh.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_BIG, self.styles.ICON_SIZE_BIG))
        self.button_refresh.setToolTip("Refresh: download new posts")
        self.button_refresh.setAccessibleName('toolbar_round_button')

        # Percentage calculation button
        self.button_calculate_percentage = QtWidgets.QPushButton()
        self.button_calculate_percentage.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, "images/stats.png")))
        self.button_calculate_percentage.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_BIG, self.styles.ICON_SIZE_BIG))
        self.button_calculate_percentage.setToolTip("Re-calculate Hot Paperness")
        self.button_calculate_percentage.setAccessibleName('toolbar_round_button')

        # Button to display new articles, or view them all
        self.button_search_new = QtWidgets.QPushButton('View unread')
        self.button_search_new.setToolTip("Display unread or all articles")
        self.button_search_new.setAccessibleName('toolbar_text_button')

        # Button to change the sorting method of the articles
        self.button_sort_by = QtWidgets.QPushButton()
        self.button_sort_by.setToolTip("Sort articles by date or Hot Paperness")
        self.button_sort_by.clicked.connect(lambda: self.changeSortingMethod(None, self.sortingReversedAction.isChecked()))
        self.button_sort_by.setAccessibleName('toolbar_text_button')

        # Create a research bar and set its size
        self.line_research = ButtonLineIcon(os.path.join(self.resource_dir, 'images/remove'), self)
        self.line_research.setToolTip("Quick search: topic or author")
        self.line_research.setPlaceholderText("Quick search")
        self.line_research.setFixedSize(self.line_research.sizeHint().width(), self.line_research.sizeHint().height() * 1.3)

        # Advanced search button
        self.button_advanced_search = QtWidgets.QPushButton()
        self.button_advanced_search.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, "images/advanced_search.png")))
        self.button_advanced_search.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_BIG, self.styles.ICON_SIZE_BIG))
        self.button_advanced_search.setToolTip("Create filters")
        self.button_advanced_search.setAccessibleName('toolbar_round_button')

        self.button_settings = QtWidgets.QPushButton()
        self.button_settings.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, "images/settings.png")))
        self.button_settings.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_BIG, self.styles.ICON_SIZE_BIG))
        self.button_settings.setToolTip("Preferences, settings")
        self.button_settings.setAccessibleName('toolbar_round_button')

        # Empty widget acting like a spacer
        self.empty_widget = QtWidgets.QWidget()
        self.empty_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Preferred)

        self.toolbar.addWidget(self.button_refresh)
        self.toolbar.addWidget(self.button_calculate_percentage)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.button_search_new)
        self.toolbar.addWidget(self.button_sort_by)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.line_research)
        self.toolbar.addWidget(self.button_advanced_search)
        self.toolbar.addWidget(self.empty_widget)
        self.toolbar.addWidget(self.button_settings)


        # ------------------------- LEFT AREA --------------------------------

        # Create scrollarea to put the journals buttons
        self.scroll_tags = QtWidgets.QScrollArea()

        # Always disable the horizontal scroll bar of the left dock
        self.scroll_tags.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)

        # Create scrolling zone
        # http://www.mattmurrayanimation.com/archives/tag/how-do-i-use-a-qscrollarea-in-pyqt
        self.scrolling_tags = QtWidgets.QWidget()

        self.vbox_all_tags = QtWidgets.QVBoxLayout()
        self.scrolling_tags.setLayout(self.vbox_all_tags)

        self.scroll_tags.hide()

        # ------------------------- RIGHT TOP AREA ---------------------------

        # Creation of a gridLayout to handle the top right area
        self.area_right_top = QtWidgets.QWidget()
        self.grid_area_right_top = QtWidgets.QGridLayout()
        self.grid_area_right_top.setContentsMargins(10, 0, 0, 0)
        self.area_right_top.setLayout(self.grid_area_right_top)

        # Here I set a prelabel: a label w/ just "Title: " to label the title.
        # I set the sizePolicy of this prelabel to the minimum. It will stretch
        # to the minimum. Makes the display better with the grid
        prelabel_title = QtWidgets.QLabel("Title: ")
        prelabel_title.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.label_title = QtWidgets.QLabel()
        self.label_title.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.label_title.setWordWrap(True)
        self.label_title.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        prelabel_author = QtWidgets.QLabel("Author(s): ")
        prelabel_author.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.label_author = QtWidgets.QLabel()
        self.label_author.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.label_author.setWordWrap(True)
        self.label_author.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        prelabel_journal = QtWidgets.QLabel("Journal: ")
        prelabel_journal.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.label_journal = QtWidgets.QLabel()
        self.label_journal.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.label_journal.setWordWrap(True)
        self.label_journal.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        prelabel_date = QtWidgets.QLabel("Date: ")
        prelabel_date.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.label_date = QtWidgets.QLabel()
        self.label_date.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.label_date.setWordWrap(True)
        self.label_date.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        prelabel_doi = QtWidgets.QLabel("DOI: ")
        prelabel_doi.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                   QtWidgets.QSizePolicy.Minimum))
        self.label_doi = QtWidgets.QLabel()
        self.label_doi.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_doi.setWordWrap(True)
        self.label_doi.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        # Buttons for the display of the article: zoom & dark background
        self.button_zoom_less = QtWidgets.QPushButton()
        self.button_zoom_less.setToolTip("Zoom out")
        self.button_zoom_less.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, 'images/zoom_out.png')))
        self.button_zoom_less.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_SMALL, self.styles.ICON_SIZE_SMALL))
        self.button_zoom_less.setAccessibleName('round_button_article')
        self.button_zoom_less.hide()
        self.button_zoom_more = QtWidgets.QPushButton()
        self.button_zoom_more.setToolTip("Zoom in")
        self.button_zoom_more.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, 'images/zoom_in.png')))
        self.button_zoom_more.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_SMALL, self.styles.ICON_SIZE_SMALL))
        self.button_zoom_more.setAccessibleName('round_button_article')
        self.button_zoom_more.hide()

        # Button to share on twitter
        self.button_twitter = QtWidgets.QPushButton()
        self.button_twitter.setToolTip("Tweet this article")
        self.button_twitter.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, 'images/twitter.png')))
        self.button_twitter.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_SMALL, self.styles.ICON_SIZE_SMALL))
        self.button_twitter.setAccessibleName('round_button_article')
        self.button_twitter.hide()

        # Button to share by email
        self.button_share_mail = QtWidgets.QPushButton()
        self.button_share_mail.setToolTip("Share by mail")
        self.button_share_mail.setIcon(QtGui.QIcon(os.path.join(self.resource_dir, 'images/email.png')))
        self.button_share_mail.setIconSize(QtCore.QSize(self.styles.ICON_SIZE_SMALL, self.styles.ICON_SIZE_SMALL))
        self.button_share_mail.setAccessibleName('round_button_article')
        self.button_share_mail.hide()

        # A personal QTextBrowser to render the sometimes rich text of the
        # abstracts
        self.text_abstract = TextBrowserPerso(self)

        # Building the grid
        self.grid_area_right_top.addWidget(prelabel_title, 0, 0, 1, 4)
        self.grid_area_right_top.addWidget(self.label_title, 0, 1)
        self.grid_area_right_top.addWidget(prelabel_author, 1, 0)
        self.grid_area_right_top.addWidget(self.label_author, 1, 1, 1, 4)
        self.grid_area_right_top.addWidget(prelabel_journal, 2, 0)
        self.grid_area_right_top.addWidget(self.label_journal, 2, 1, 1, 4)
        self.grid_area_right_top.addWidget(prelabel_date, 3, 0)
        self.grid_area_right_top.addWidget(self.label_date, 3, 1, 1, 4)
        self.grid_area_right_top.addWidget(prelabel_doi, 4, 0)
        self.grid_area_right_top.addWidget(self.label_doi, 4, 1, 1, 4)

        # An empty widget, acts as spacer
        self.empty_widget = QtWidgets.QWidget()
        self.empty_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # A HBoxLayout to store the article "toolbar"
        self.hbox_toolbar_article = QtWidgets.QHBoxLayout()
        self.hbox_toolbar_article.addWidget(self.button_zoom_less, alignment=QtCore.Qt.AlignLeft)
        self.hbox_toolbar_article.addWidget(self.button_zoom_more, alignment=QtCore.Qt.AlignLeft)
        self.hbox_toolbar_article.addWidget(self.empty_widget)
        self.hbox_toolbar_article.addWidget(self.button_twitter, alignment=QtCore.Qt.AlignRight)
        self.hbox_toolbar_article.addWidget(self.button_share_mail, alignment=QtCore.Qt.AlignRight)

        self.grid_area_right_top.addLayout(self.hbox_toolbar_article, 5, 0, 1, 4)
        self.grid_area_right_top.addWidget(self.text_abstract, 6, 0, 1, 4)

        # USEFULL: set the size of the grid and its widgets to the minimum
        self.grid_area_right_top.setRowStretch(6, 1)

        # ------------------------- ASSEMBLING THE AREAS ----------------------

        # Main part of the window in a tab.
        # Allows to create other tabs
        self.onglets = TabPerso(self)

        self.central_widget = QtWidgets.QWidget()
        self.hbox_central = QtWidgets.QHBoxLayout()
        # (int left, int top, int right, int bottom) getContentsMargins (self)
        self.hbox_central.setContentsMargins(0, 5, 0, 5)
        self.central_widget.setLayout(self.hbox_central)

        self.splitter2 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.area_right_top)

        self.hbox_central.addWidget(self.scroll_tags)
        self.hbox_central.addWidget(self.splitter2)

        # Create the main table, at index 0
        self.createSearchTab("All articles", "SELECT * FROM papers")

        self.setCentralWidget(self.central_widget)

        # Stylesheet for general style
        stylesheet = self.styles.styleGeneral()
        self.central_widget.setStyleSheet(stylesheet)
        self.toolbar.setStyleSheet(stylesheet)

        # Stylesheet for the toolbar
        stylesheet = self.styles.styleToolbar()
        self.button_search_new.setStyleSheet(stylesheet)
        self.button_sort_by.setStyleSheet(stylesheet)
        self.line_research.setStyleSheet(stylesheet)
        self.button_refresh.setStyleSheet(stylesheet)
        self.button_calculate_percentage.setStyleSheet(stylesheet)
        self.button_advanced_search.setStyleSheet(stylesheet)
        self.button_settings.setStyleSheet(stylesheet)

        # Stylesheet for the buttons
        stylesheet = self.styles.styleButtons()
        self.scroll_tags.setStyleSheet(stylesheet)
        self.button_twitter.setStyleSheet(stylesheet)
        self.button_share_mail.setStyleSheet(stylesheet)
        self.button_zoom_less.setStyleSheet(stylesheet)
        self.button_zoom_more.setStyleSheet(stylesheet)


if __name__ == '__main__':
    # logger = MyLog()
    # try:
    app = QtWidgets.QApplication(sys.argv)

    # ex = Fenetre(logger)
    ex = MyWindow()
    app.processEvents()
    sys.exit(app.exec_())
