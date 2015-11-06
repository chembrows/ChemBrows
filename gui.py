#!/usr/bin/python
# coding: utf-8


import sys
import os
from PyQt4 import QtGui, QtSql, QtCore
import datetime
import urllib
import fnmatch
import webbrowser
import requests

# To package and distribute the program
import esky

# Personal modules
from log import MyLog
from model import ModelPerso
from view import ViewPerso
from web_view import WebViewPerso
from view_delegate import ViewDelegate
from worker import Worker
from predictor import Predictor
from settings import Settings
from advanced_search import AdvancedSearch
from tab import TabPerso
import functions
import hosts
from updater import Updater
from line_clear import ButtonLineEdit
from signing import Signing
from tuto import Tuto
from my_twit import MyTwit

# TEST
import constants

# To debug and profile. Comment for prod
# from memory_profiler import profile


class Fenetre(QtGui.QMainWindow):

    # def __init__(self, logger):
    def __init__(self):

        super(Fenetre, self).__init__()

        # Display a splash screen when booting
        # http://eli.thegreenplace.net/2009/05/09/creating-splash-screens-in-pyqt
        # CAREFUL, there is a bug with the splash screen
        # https://bugreports.qt.io/browse/QTBUG-24910
        splash_pix = QtGui.QPixmap('./images/splash.png')
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()

        # Check if the running ChemBrows is a frozen app
        if getattr(sys, "frozen", False):
            # The program is NOT in debug mod if it's frozen
            self.debug_mod = False
            self.DATA_PATH = constants.DATA_PATH

            # Create the user directory if it doesn't exist
            os.makedirs(self.DATA_PATH, exist_ok=True)

        else:
            # The program is in debug mod if it's not frozen
            self.debug_mod = True
            self.DATA_PATH = "."

        # Create the logger
        self.l = MyLog(self.DATA_PATH + "/activity.log")
        # self.l.setLevel(20)
        self.l.info('Starting the program')

        if self.debug_mod:
            self.l.info("You are running ChemBrows in debug mode")
            self.l.info("This version of ChemBrows is NOT a frozen version")
        else:
            self.l.info("This version of ChemBrows is a frozen version")

        # Bool to check if the program is collecting data
        self.parsing = False

        QtGui.qApp.installEventFilter(self)

        # List to store the tags checked
        self.tags_selected = []

        # List to store all the views, models and proxies
        self.list_tables_in_tabs = []
        self.list_proxies_in_tabs = []

        # Call processEvents regularly for the splash screen
        start_time = datetime.datetime.now()

        diff_time = start_time

        # Look for updates and create files
        app.processEvents()
        self.bootCheckList()
        self.l.debug("bootCheckList took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()


        # Object to store options and preferences
        self.options = QtCore.QSettings(self.DATA_PATH + "/config/options.ini", QtCore.QSettings.IniFormat)

        # Connect to the database & log the connection
        app.processEvents()
        self.connectionBdd()
        self.defineActions()
        self.logConnection()
        self.l.debug("connectionBdd, defineActions & logConnection took {}"
                     .format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Create the GUI
        app.processEvents()
        self.initUI()
        self.l.debug("initUI took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Define the slots
        app.processEvents()
        self.defineSlots()
        self.l.debug("defineSlots took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Creates the journals buttons
        app.processEvents()
        self.displayTags()
        self.l.debug("displayTags took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Restore the settings
        app.processEvents()
        self.restoreSettings()
        self.l.debug("restoreSettings took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        # Load the notifications
        app.processEvents()
        self.loadNotifications()
        self.l.debug("loadNotifications took {}".
                     format(datetime.datetime.now() - diff_time))
        diff_time = datetime.datetime.now()

        app.processEvents()

        # Show the window
        self.show()
        splash.finish(self)
        self.l.debug("splash.finish() took {}".
                     format(datetime.datetime.now() - diff_time))

        self.l.info("Boot took {}".
                    format(datetime.datetime.now() - start_time))

        self.finishBoot()


    def bootCheckList(self):

        """Performs some startup checks"""

        # Create the folder to store the graphical_abstracts if
        # it doesn't exist
        # http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
        os.makedirs(self.DATA_PATH + '/graphical_abstracts', exist_ok=True)

        # Check if the running ChemBrows is a frozen app
        if not self.debug_mod:

            update = Updater(self.l)

            if update is None:
                return

            # If an update is available, ask the user if he wants to
            # update immediately
            if update.update_available:

                message = "A new version of ChemBrows is available. Upgrade now ?"
                choice = QtGui.QMessageBox.question(self, "Update of ChemBrows", message,
                                                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok,
                                                    defaultButton=QtGui.QMessageBox.Ok)

                # If the user says yes, start the update
                if choice == QtGui.QMessageBox.Ok:
                    self.l.info("Starting update")

                    def whenDone():

                        """Slot called when the update id finished"""

                        self.l.info("Update finished")
                        self.progress.reset()

                        # Display a dialog box to tell the user to restart the program
                        message = "ChemBrows is now up-to-date. Restart it to use the last version"
                        QtGui.QMessageBox.information(self, "ChemBrows update", message, QtGui.QMessageBox.Ok)

                        del update

                    # Display a QProgressBar while updating
                    app.processEvents()
                    self.progress = QtGui.QProgressDialog("Updating ChemBrows...", None, 0, 0, self)
                    self.progress.setWindowTitle("Updating")
                    self.progress.show()
                    app.processEvents()

                    update.finished.connect(whenDone)
                    update.start()


    def logConnection(self):

        """Originally, coded to perform check acces on the server. If
        the programm doesn't go commercial, RENAME THIS METHOD.
        For now, this method get the max id, used to know if incoming articles
        are new"""

        # Check if there is a user_id. If so, log the connection
        user_id = self.options.value("user_id", None)
        if user_id is None:
            self.max_id_for_new = 0
            return

        count_query = QtSql.QSqlQuery(self.bdd)

        count_query.exec_("SELECT COUNT(id) FROM papers")
        count_query.first()
        nbr_entries = count_query.record().value(0)
        self.l.info("Nbr of entries: {}".format(nbr_entries))

        count_query.exec_("SELECT MAX(id) FROM papers")
        count_query.first()
        self.max_id_for_new = count_query.record().value(0)

        if type(self.max_id_for_new) is not int:
            self.max_id_for_new = 0

        self.l.info("Max id for new: {}".format(self.max_id_for_new))

        payload = {'nbr_entries': nbr_entries,
                   'journals': self.getJournalsToCare(),
                   'user_id': user_id,
                  }

        try:
            if self.debug_mod:
                req = requests.post('http://chembrows.com/cgi-bin/log.py', params=payload, timeout=1)
            else:
                req = requests.post('http://chembrows.com/cgi-bin/log.py', params=payload, timeout=3)
            self.l.info(req.text)
        except requests.exceptions.ReadTimeout:
            self.l.error("checkAccess. ReadTimeout while contacting the server")
            return
        except requests.exceptions.ConnectTimeout:
            self.l.error("checkAccess. ConnectionTimeout while contacting the server")
            return


    def finishBoot(self):

        """Method to register a new user. When it is done,
        start the tutorial"""

        # Check if there is a user_id. If not, register the user
        if self.options.value("user_id", None) is None:

            sign = Signing(self)

            # When the user is registered, start the tuto
            sign.accepted.connect(lambda: Tuto(self))


    def showAbout(self):

        """Shows a dialogBox w/ the version number"""

        with open('config/version.txt', 'r') as version_file:
            version = version_file.read()
        message = "You are using ChemBrows version {}\nwww.chembrows.com".format(version)
        QtGui.QMessageBox.about(self, "About ChemBrows", message)


    def connectionBdd(self):

        """Method to connect to the database. Creates it
        if it does not exist"""

        # Set the database
        self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.bdd.setDatabaseName(self.DATA_PATH + "/fichiers.sqlite")

        self.bdd.open()

        query = QtSql.QSqlQuery(self.bdd)
        query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                     doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                     liked INTEGER, url TEXT, new INTEGER, topic_simple TEXT)")

        if self.debug_mod:
            query.exec_("CREATE TABLE IF NOT EXISTS debug \
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, doi TEXT, \
                        title TEXT, journal TEXT, url TEXT)")

        # Create the model for the new tab
        self.model = ModelPerso(self)

        # Changes are not effective immediately, but it doesn't matter
        # because the view is updated each time a change is made
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)

        self.model.setTable("papers")
        self.model.select()


    def getJournalsToCare(self):

        """Get the journals checked in the settings window"""

        # Create a list to store the journals checked in the settings window
        journals = self.options.value("journals_to_parse", [])

        # If no journals to care in the settings,
        # take them all. So build a journals_to_care list
        # with all the journals
        if not journals:
            # self.journals_to_care = []
            for company in os.listdir("./journals"):
                with open('./journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        # Take the abbreviation
                        journals.append(line.split(" : ")[1])

        return journals


    def parse(self):

        """Method to start the parsing of the data"""

        self.parsing = True

        self.journals_to_parse = self.options.value("journals_to_parse", [])

        # If no journals to parse in the settings,
        # parse them all. So build a journals_to_parse list
        # with all the journals
        if not self.journals_to_parse:
            self.journals_to_parse = []
            for company in os.listdir("./journals"):
                with open('journals/{0}'.format(company), 'r') as config:
                    for line in config:
                        self.journals_to_parse.append(line.split(" : ")[1])

            self.options.remove("journals_to_parse")
            self.options.setValue("journals_to_parse", self.journals_to_parse)

        self.urls = []
        for company in os.listdir("./journals"):
            with open('journals/{0}'.format(company), 'r') as config:
                for line in config:
                    if line.split(" : ")[1] in self.journals_to_parse:
                        line = line.split(" : ")[2]
                        line = line.strip()
                        self.urls.append(line)

        # Create a dictionnary w/ all the data concerning the journals
        # implemented in the program: names, abbreviations, urls
        self.dict_journals = {}
        for company in os.listdir("./journals"):
            company = company.split('.')[0]
            self.dict_journals[company] = hosts.getJournals(company)

        # Disabling the parse action to avoid double start
        self.parseAction.setEnabled(False)

        self.start_time = datetime.datetime.now()

        # Display a progress dialog box
        self.progress = QtGui.QProgressDialog("Collecting in progress", None, 0, 100, self)
        self.progress.setWindowTitle("Collecting articles")
        self.progress.show()

        self.urls_max = len(self.urls)

        # Get the optimal nbr of thread. Will vary depending
        # on the user's computer
        max_nbr_threads = QtCore.QThread.idealThreadCount()
        self.l.debug("IdealThreadCount: {}".format(max_nbr_threads))
        # max_nbr_threads = 1

        # # Start a sql transaction here. Will commit all the bdd
        # # changes when the parsing is finished
        # self.bdd.transaction()

        # Counter to count the new entries in the database
        self.counter = 0
        self.counter_updates = 0
        self.counter_rejected = 0

        # # List to store the threads.
        # # The list is cleared when the method is started
        self.list_threads = []
        self.count_threads = 0
        for i in range(max_nbr_threads):
            try:
                url = self.urls[i]
                worker = Worker(self.l, self.bdd, self.dict_journals, self)
                worker.setUrl(url)
                worker.finished.connect(self.checkThreads)
                self.urls.remove(url)
                self.list_threads.append(worker)
                worker.start()
                app.processEvents()
            except IndexError:
                break


    # @profile
    def checkThreads(self):

        """Method to check the state of each thread.
        If all the threads are finished, enable the parse action.
        This slot is called when a thread is finished, to start the
        next one"""

        elapsed_time = datetime.datetime.now() - self.start_time
        self.l.info(elapsed_time)

        self.count_threads += 1

        for worker in self.list_threads:
            if worker.isFinished():
                self.list_threads.remove(worker)
                del worker

        # Display the nbr of finished threads
        self.l.info("Done: {}/{}".format(self.count_threads, self.urls_max))

        # # Display the progress of the parsing w/ the progress bar
        percent = self.count_threads * 100 / self.urls_max

        self.progress.setValue(round(percent, 0))
        if percent >= 100:
            self.progress.reset()
            app.processEvents()

        if self.count_threads == self.urls_max:

            self.l.info("{} new entries added to the database".format(self.counter))
            self.l.info("{} entries rejected".format(self.counter_rejected))
            self.l.info("{} attempts to update entries".format(self.counter_updates))

            self.calculatePercentageMatch(update=False)
            self.parseAction.setEnabled(True)
            self.l.info("Parsing data finished. Enabling parseAction")

            self.loadNotifications()

            # Update the view when a worker is finished
            self.searchByButton()
            self.updateCellSize()
            self.parsing = False

            self.list_tables_in_tabs[0].verticalScrollBar().setSliderPosition(0)

        else:
            if self.urls:
                self.l.debug("STARTING NEW THREAD")
                worker = Worker(self.l, self.bdd, self.dict_journals, self)
                worker.setUrl(self.urls[0])
                worker.finished.connect(self.checkThreads)
                self.urls.remove(worker.url_feed)
                self.list_threads.append(worker)
                worker.start()
                app.processEvents()


    def defineActions(self):

        """On définit ici les actions du programme. Cette méthode est
        appelée à la création de la classe"""

        # Action to quit
        self.exitAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_063_power'), '&Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Quit")
        self.exitAction.triggered.connect(self.closeEvent)

        # Action to refresh the posts
        self.parseAction = QtGui.QAction('&Refresh', self)
        self.parseAction.setShortcut('F5')
        self.parseAction.setToolTip("Refresh: download new posts")
        self.parseAction.triggered.connect(self.parse)

        # Action to calculate the percentages of match
        self.calculatePercentageMatchAction = QtGui.QAction('&Percentages', self)
        self.calculatePercentageMatchAction.setShortcut('F6')
        self.calculatePercentageMatchAction.setToolTip("Re-calculate Hot Paperness")
        self.calculatePercentageMatchAction.triggered.connect(lambda: self.calculatePercentageMatch(update=True))

        # Action to like a post
        self.toggleLikeAction = QtGui.QAction('Toggle like', self)
        self.toggleLikeAction.setShortcut('L')
        self.toggleLikeAction.triggered.connect(self.toggleLike)

        # Action to open the post in browser
        self.openInBrowserAction = QtGui.QAction('Open post in browser', self)
        self.openInBrowserAction.triggered.connect(self.openInBrowser)
        self.openInBrowserAction.setShortcut('Ctrl+W')

        # Action to update the model. For TEST
        # self.updateAction = QtGui.QAction('Update model', self)
        # self.updateAction.triggered.connect(self.updateModel)
        # self.updateAction.setShortcut('F7')

        # Action to show a settings window
        self.settingsAction = QtGui.QAction('Preferences', self)
        self.settingsAction.triggered.connect(lambda: Settings(self))

        self.tutoAction = QtGui.QAction('Tutorial', self)
        self.tutoAction.triggered.connect(lambda: Tuto(self))

        # Action to show a settings window
        self.showAboutAction = QtGui.QAction('About', self)
        self.showAboutAction.triggered.connect(self.showAbout)

        # # Action so show new articles
        # self.searchNewAction = QtGui.QAction('View unread', self)
        # self.searchNewAction.setToolTip("Display unread articles")
        # self.searchNewAction.triggered.connect(self.searchNew)

        # Action to toggle the read state of an article
        self.toggleReadAction = QtGui.QAction('Toggle read', self)
        self.toggleReadAction.setShortcut('M')
        self.toggleReadAction.triggered.connect(self.toggleRead)

        # Start advanced search
        self.advanced_searchAction = QtGui.QAction(QtGui.QIcon('images/glyphicons_025_binoculars'), 'Advanced search', self)
        self.advanced_searchAction.setToolTip("Advanced earch")
        self.advanced_searchAction.triggered.connect(lambda: AdvancedSearch(self))

        # Action to change the sorting method of the views. In the menu
        self.sortingPercentageAction = QtGui.QAction('By Hot Paperness', self, checkable=True)
        self.sortingPercentageAction.triggered.connect(lambda: self.changeSortingMethod(0))

        # Action to change the sorting method of the views. In the menu
        self.sortingDateAction = QtGui.QAction('By date', self, checkable=True)
        self.sortingDateAction.triggered.connect(lambda: self.changeSortingMethod(1))

        # Action to change the sorting method of the views, reverse the results. In the menu
        self.sortingReversedAction = QtGui.QAction('Reverse order', self, checkable=True)
        self.sortingReversedAction.triggered.connect(lambda: self.changeSortingMethod(self.sorting_method, True))

        # Action to change the sorting method of the views, reverse the results. In the menu
        self.emptyWaitAction = QtGui.QAction('Empty to-read list', self)
        self.emptyWaitAction.triggered.connect(self.emptyWait)

        # Action add/remove a post of the to-read list. For the right click
        self.toggleWaitAction = QtGui.QAction('Add/remove to to-read list', self)
        self.toggleWaitAction.triggered.connect(self.toggleWait)

        # Action to serve use as a separator
        self.separatorAction = QtGui.QAction(self)
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

        self.list_tables_in_tabs[0].verticalScrollBar().setSliderPosition(0)

        # for table in self.list_tables_in_tabs:
            # Qt.AscendingOrder   0   starts with 'AAA' ends with 'ZZZ'
            # Qt.DescendingOrder  1   starts with 'ZZZ' ends with 'AAA'
            # if "reverse order" in unchecked, reverse = False = 0
            # -> 1 - reverse = 1 -> DescendingOrder -> starts with the
            # highest percentages


    def updateModel(self):

        """Debug function, allows to update a model
        with a button, at any time. Will not be used by
        the final user"""

        self.updateView()


    # @profile
    def closeEvent(self, event):

        """Method to perform actions before exiting.
        Allows to save the prefs in a file"""

        # http://stackoverflow.com/questions/9249500/
        # pyside-pyqt-detect-if-user-trying-to-close-window

        # Save the to-read list
        if self.waiting_list.list_id_articles:
            self.options.setValue("ids_waited", self.waiting_list.list_id_articles)
        else:
            self.options.remove("ids_waited")

        # Record the window state and appearance
        self.options.beginGroup("Window")

        # Reinitializing the keys
        self.options.remove("")

        self.l.debug("Saving windows state")
        self.options.setValue("window_geometry", self.saveGeometry())
        self.options.setValue("window_state", self.saveState())

        for index, each_table in enumerate(self.list_tables_in_tabs):
            self.options.setValue("header_state{0}".format(index), each_table.horizontalHeader().saveState())

        # Save the state of the window's splitter
        self.options.setValue("final_splitter", self.splitter2.saveState())

        # Save the sorting method
        self.options.setValue("sorting_method", self.sorting_method)
        self.options.setValue("sorting_reversed", self.sorting_reversed)

        self.options.setValue("dark", self.dark)

        self.options.endGroup()

        # Be sure self.options finished its tasks.
        # Correct a bug
        self.options.sync()

        self.model.submitAll()

        # Close the database connection
        self.bdd.removeDatabase(self.DATA_PATH + "/fichiers.sqlite")
        self.bdd.close()

        QtGui.qApp.quit()

        self.l.info("Closing the program")


    # @profile
    def loadNotifications(self):

        """Method to find the number of unread articles,
        for each search. Load a list of id, for the unread articles,
        in each table. And a list of id, for the concerned articles, for
        each table"""

        count_query = QtSql.QSqlQuery(self.bdd)

        # Don't treat the articles if it's the main tab, it's
        # useless because the article will be concerned for sure
        for table in self.list_tables_in_tabs[1:]:

            # Empty these lists, because when loadNotifications is called
            # several times during the use, the nbr of unread articles is
            # added to the nbr of notifications
            table.list_new_ids = []
            table.list_id_articles = []

            # Try to speed things up
            append_new = table.list_new_ids.append
            append_articles = table.list_id_articles.append

            req_str = self.refineBaseQuery(table.base_query, table.topic_entries, table.author_entries)
            count_query.exec_(req_str)

            while count_query.next():
                record = count_query.record()

                append_articles(record.value('id'))

                if record.value('new') == 1:
                    append_new(record.value('id'))

        # Set the notifications for each tab
        for index in range(1, self.onglets.count()):
            notifs = len(self.onglets.widget(index).list_new_ids)
            self.onglets.setNotifications(index, notifs)


    def restoreSettings(self):

        """Restore the prefs of the window"""

        # Restore the to-read list
        ids_waited = self.options.value("ids_waited", [])
        self.createToRead(ids_waited)

        searches_saved = QtCore.QSettings(self.DATA_PATH + "/config/searches.ini", QtCore.QSettings.IniFormat)

        # Restore the saved searches
        for search_name in searches_saved.childGroups():
            query = searches_saved.value("{0}/sql_query".format(search_name))
            topic_entries = searches_saved.value("{0}/topic_entries".format(search_name), None)
            author_entries = searches_saved.value("{0}/author_entries".format(search_name), None)
            self.createSearchTab(search_name, query,
                                 topic_options=topic_entries,
                                 author_options=author_entries)

        # If windows settings are available, import and use them
        if "Window" in self.options.childGroups():

            self.restoreGeometry(self.options.value("Window/window_geometry"))
            self.restoreState(self.options.value("Window/window_state"))

            for index, each_table in enumerate(self.list_tables_in_tabs):
                header_state = self.options.value("Window/header_state{0}".format(index))
                if header_state is not None:
                    each_table.horizontalHeader().restoreState(self.options.value("Window/header_state{0}".format(index)))

            self.splitter2.restoreState(self.options.value("Window/final_splitter"))

            # # Bloc to restore the check of the sorting method, in the View menu
            # # of the menubar
            self.sorting_method = self.options.value("Window/sorting_method", 1, int)
            self.sorting_reversed = self.options.value("Window/sorting_reversed", False, bool)

            # Boolean: the background of the abstract zone is dark or not
            self.dark = self.options.value("Window/dark", False, bool)

            # Restore the journals selected (buttons pushed)
            self.tags_selected = self.options.value("Window/tags_selected", [])
            if self.tags_selected == self.getJournalsToCare():
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

        self.getJournalsToCare()

        self.searchByButton()

        # Timer to get the dimensions of the window right.
        # If the window is displayed too fast, I can't get the dimensions right
        QtCore.QTimer.singleShot(50, self.updateCellSize)


    def eventFilter(self, source, event):

        """Sublclassing of this method allows to hide/show
        the journals filters on the left, through a mouse hover event"""

        # do not hide menubar when menu shown
        if QtGui.qApp.activePopupWidget() is None:
            # If parsing running, block some user inputs
            if self.parsing:
                forbidden = [QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease,
                             QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick,
                             QtCore.QEvent.MouseMove, QtCore.QEvent.Wheel]
                if event.type() == QtCore.QEvent.Close:
                    self.progress.reset()
                    return False
                elif event.type() in forbidden:
                    return True
            if event.type() == QtCore.QEvent.MouseMove:
                try:
                    if self.scroll_tags.isHidden():
                        try:
                            # Calculate the top zone where resizing can't happen (menubar, toolbar, etc)
                            table_y = self.toolbar.rect().height() + self.menubar.rect().height() + \
                                    self.mapToGlobal(QtCore.QPoint(0, 0)).y() + self.hbox_central.getContentsMargins()[1]
                        except AttributeError:
                            pass
                        rect = self.geometry()
                        rect.setWidth(25)
                        rect.setTop(table_y)

                        if rect.contains(event.globalPos()):
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
                    self.l.debug("Event filter, AttributeError, probably starting the program")

            elif event.type() == QtCore.QEvent.Leave and source is self:
                self.scroll_tags.hide()
                self.updateCellSize()

        return QtGui.QMainWindow.eventFilter(self, source, event)


    def resizeEvent(self, event):

        """Called when the Main window is resized.
        Reimplemented to resize the cell when the window
        is resized"""

        super(Fenetre, self).resizeEvent(event)

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
        menu = QtGui.QMenu()
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

        self.button_color_read.clicked.connect(self.text_abstract.darkAndLight)

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

        # for table in self.list_tables_in_tabs:
            # table.verticalHeader().setDefaultSectionSize(table.height() * 0.2)


    def displayInfos(self):

        """Method to get the infos of a post. Also loads the graphical abstract.
        Basically build the infos displayed on the right side"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # Get the different infos for an article
        title = table.model().index(table.selectionModel().selection().indexes()[0].row(), 3).data()
        author = table.model().index(table.selectionModel().selection().indexes()[0].row(), 6).data()
        date = table.model().index(table.selectionModel().selection().indexes()[0].row(), 4).data()
        journal = table.model().index(table.selectionModel().selection().indexes()[0].row(), 5).data()

        abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 7).data()

        try:
            # Checkings on the graphical abstract. Add the path of the picture to
            # the abstract if ok
            graphical_abstract = table.model().index(table.selectionModel().selection().indexes()[0].row(), 8).data()
            if type(graphical_abstract) is str and graphical_abstract != "Empty":
                # Get the path of the graphical abstract
                base = "<br/><br/><p align='center'><img src='file:///{}' align='center' /></p>"
                base = base.format(os.path.abspath(self.DATA_PATH + "/graphical_abstracts/" + graphical_abstract))
                abstract += base
        except TypeError:
            self.l.debug("No graphical abstract for this post, displayInfos()")

        self.button_zoom_less.show()
        self.button_zoom_more.show()
        self.button_color_read.show()
        self.button_twitter.show()
        self.button_share_mail.show()

        self.label_date.setText(date)
        self.label_title.setText("<span style='font-size:12pt; font-weight:bold'>{0}</span>".format(title))
        self.label_journal.setText(journal)

        if type(abstract) is str:
            self.text_abstract.setHtml(abstract)
        else:
            self.text_abstract.setHtml("")

        if type(author) is str:
            self.label_author.setText(author)
        else:
            self.label_author.setText("")


    def tabChanged(self):

        """Slot to perform some actions when the current tab is changed.
        Mainly sets the tab query to the saved query"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        table.updateHeight()

        # Submit the changes on the model.
        # Otherwise, a bug appears: one changing an article, the changes are visible
        # (trough the proxy) on all the articles at the same place in all tabs
        self.model.submitAll()

        self.searchByButton()

        self.button_search_new.setText("View unread")
        for proxy in self.list_proxies_in_tabs:
            proxy.setFilterRegExp(QtCore.QRegExp('[01]'))
            proxy.setFilterKeyColumn(11)

        # Update the size of the columns of the view if the central
        # splitter moved
        self.updateCellSize()


    def createToRead(self, list_ids):

        proxy = QtGui.QSortFilterProxyModel()

        proxy.setSourceModel(self.model)
        self.list_proxies_in_tabs.append(proxy)

        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.name_search = "To read"

        requete = "SELECT * FROM papers WHERE id IN("

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

        # Define an attribute for the to read list
        self.waiting_list = tableau

        self.onglets.addTab(tableau, "To read")


    def createSearchTab(self, name_search, query, topic_options=None, author_options=None, update=False):

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
                    break

            if self.onglets.tabText(self.onglets.currentIndex()) == name_search:
                self.searchByButton()
            else:
                self.updateView()

            self.loadNotifications()

            return

        proxy = QtGui.QSortFilterProxyModel()

        # TESTING
        # W/ a non dynamic sorting filter, I can use
        # the proxy to filter the new articles, which is much
        # faster than doing a query

        proxy.setSourceModel(self.model)
        self.list_proxies_in_tabs.append(proxy)


        # Create the view, and give it the model
        tableau = ViewPerso(self)
        tableau.name_search = name_search
        tableau.base_query = query
        tableau.topic_entries = topic_options
        tableau.author_entries = author_options
        tableau.setModel(proxy)
        tableau.setItemDelegate(ViewDelegate(self))
        tableau.setSelectionBehavior(tableau.SelectRows)
        tableau.updateHeight()
        tableau.initUI()

        self.list_tables_in_tabs.append(tableau)

        self.onglets.addTab(tableau, name_search)


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

        journals_to_care = self.getJournalsToCare()

        if not journals_to_care:
            return

        journals_to_care.sort()

        size = 0

        for journal in journals_to_care:

            button = QtGui.QPushButton(journal)
            button.setCheckable(True)
            button.adjustSize()

            if button.width() > size:
                size = button.width()

            button.clicked[bool].connect(self.stateButtons)
            self.vbox_all_tags.addWidget(button)

            self.list_buttons_tags.append(button)

        self.vbox_all_tags.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_tags.setWidget(self.scrolling_tags)

        # Get the pixles which need to be added
        # +10 because of margin-left for the buttons
        add = self.vbox_all_tags.getContentsMargins()[0] * 2 + 2 + 10 + \
            self.scroll_tags.verticalScrollBar().sizeHint().width()

        # self.scroll_tags.setFixedWidth(size + add)
        self.scroll_tags.setFixedWidth(size + add)

        self.scrolling_tags.adjustSize()


    def stateButtons(self, pressed):

        """Slot to check the journals push buttons"""

        if self.tags_selected == self.getJournalsToCare():
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

        # When last button is uncheck, select all the journals
        if not self.tags_selected:
            self.tags_selected = self.getJournalsToCare()

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        # Update the base query of the to-read list
        if table is self.waiting_list:
            requete = "SELECT * FROM papers WHERE id IN("
            for each_id in table.list_id_articles:
                if each_id != table.list_id_articles[-1]:
                    requete = requete + str(each_id) + ", "
                else:
                    requete = requete + str(each_id) + ")"
            table.base_query = requete

        self.query = QtSql.QSqlQuery(self.bdd)

        # The normal query:
        # SELECT * FROM papers WHERE topic_simple LIKE '% carboxyfluorescein %'
        # Becomes:
        # SELECT * FROM papers WHERE (topic_simple LIKE '% carboxyfluorescein %') AND journal IN ("ACS Catal."...

        refined_query = self.refineBaseQuery(table.base_query, table.topic_entries, table.author_entries)

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
            for proxy in self.list_proxies_in_tabs:
                proxy.setFilterRegExp(QtCore.QRegExp('[01]'))
                proxy.setFilterKeyColumn(11)

        self.list_tables_in_tabs[0].verticalScrollBar().setSliderPosition(0)


    def refineBaseQuery(self, base_query, topic_options, author_options):

        """Method to refine the base_query of a view.
        A normal SQL query can't search a comma-separated list, so
        the results of the SQL query are filtered afterwords"""

        author_entries = author_options

        # If no * in the SQL query, return
        if author_entries is None or not any('*' in element for element in author_entries):
            return base_query

        query = QtSql.QSqlQuery(self.bdd)
        query.prepare(base_query)
        query.exec_()

        # Prepare a list to store the filtered items
        list_ids = []

        while query.next():
            record = query.record()

            # Normalize the authors string of the item
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
                    if index == 0:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if not matching:
                                adding = False
                                break

                    # OR condition
                    if index == 1:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                list_adding_or.append(True)
                                break
                            else:
                                list_adding_or.append(False)

                        else:
                            # Tips for any()
                            # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
                            if any(person in element for element in authors):
                                list_adding_or.append(True)
                            else:
                                list_adding_or.append(False)

                    # NOT condition
                    if index == 2:
                        if '*' in person:
                            matching = fnmatch.filter(authors, person)
                            if matching:
                                adding = False
                                break
                        else:
                            if any(person in element for element in authors):
                                adding = False

                if True not in list_adding_or and list_adding_or:
                    adding = False
                if not adding:
                    continue

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
                    requete = requete + "\"" + str(each_id) + "\"" + ", "
                # Close the query if last
                else:
                    requete = requete + "\"" + str(each_id) + "\"" + ")"

            return requete


    def research(self):

        """Slot to search on title and abstract.
        The search can be performed on a particular tab"""

        # If it's not the main tab, filter through the already-filtered
        # results of a particular tab
        if self.onglets.currentIndex() != 0:
            table = self.list_tables_in_tabs[self.onglets.currentIndex()]
            requete = self.refineBaseQuery(table.base_query, table.topic_entries, table.author_entries)
            requete = requete.replace("WHERE ", "WHERE (")
            requete += ") AND (topic_simple LIKE '%{}%') AND journal IN ("
        else:
            requete = "SELECT * FROM papers WHERE (topic_simple LIKE '%{}%') AND journal IN ("

        results = functions.simpleChar(self.line_research.text())

        self.query = QtSql.QSqlQuery(self.bdd)

        # Search only the selected journals
        for each_journal in self.tags_selected:
            if each_journal != self.tags_selected[-1]:
                requete = requete + "\"" + str(each_journal) + "\"" + ", "
            else:
                requete = requete + "\"" + str(each_journal) + "\"" + ")"

        self.query.prepare(requete.format(results))
        self.query.exec_()

        self.updateView()


    def clearSearch(self):

        """Method to clear the research bar"""

        self.line_research.clear()
        self.line_research.returnPressed.emit()


    def clearLayout(self, layout):

        """Method to erase the widgets from a layout"""

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                    QtGui.QApplication.processEvents()
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
        self.text_abstract.setHtml("")

        # Uncheck the journals buttons on the left
        for button in self.list_buttons_tags:
            button.setChecked(False)

        for proxy in self.list_proxies_in_tabs:
            proxy.setFilterRegExp(QtCore.QRegExp('[01]'))
            proxy.setFilterKeyColumn(11)

        self.tags_selected = self.getJournalsToCare()
        self.searchByButton()

        # Clear the search bar
        self.line_research.clear()

        self.button_zoom_less.hide()
        self.button_zoom_more.hide()
        self.button_color_read.hide()
        self.button_twitter.hide()
        self.button_share_mail.hide()

        # Put the vertical scroll bar at the top
        self.list_tables_in_tabs[0].verticalScrollBar().setSliderPosition(0)

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
            if id_bdd in self.onglets.widget(index).list_new_ids and remove:
                self.onglets.widget(index).list_new_ids.remove(id_bdd)

            # Add the id to the list of new articles
            elif id_bdd in self.onglets.widget(index).list_id_articles and not remove:
                self.onglets.widget(index).list_new_ids.append(id_bdd)

            notifs = len(self.onglets.widget(index).list_new_ids)
            self.onglets.setNotifications(index, notifs)


    def markOneRead(self, element):

        """Slot to mark an article read"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        id_bdd = table.model().index(element.row(), 0).data()
        new = table.model().index(element.row(), 11).data()

        # update_new: to check if the user is currently clicking
        # on the read icon. If so, don't mark the article as read
        if new == 0 or table.update_new == True:
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

        """Method to put/unput an article in the To-read list"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]
        line = table.selectionModel().currentIndex().row()
        id_bdd = table.model().index(line, 0).data()
        new = table.model().index(line, 11).data()
        waited = id_bdd in self.waiting_list.list_id_articles

        # Check if the to read list is empty
        empty = self.waiting_list.list_id_articles == []

        if waited:
            self.waiting_list.list_id_articles.remove(id_bdd)

            # The post is not a new post in the to read list anymore
            if id_bdd in self.waiting_list.list_new_ids:
                self.waiting_list.list_new_ids.remove(id_bdd)

            # Immediately visually remove the post from the to read list
            # if the to read list is displayed
            if table is self.waiting_list:
                self.searchByButton()

                # Update the cells bc the scroll bar can disappear when
                # posts are removed from the to read list
                self.updateCellSize()

            self.updateNotifications(id_bdd)
        else:
            self.waiting_list.list_id_articles.append(id_bdd)

            if new == 1:
                self.waiting_list.list_new_ids.append(id_bdd)

        # Update the notifications of the to-read list
        index = self.list_tables_in_tabs.index(self.waiting_list)
        self.onglets.setNotifications(index, len(self.waiting_list.list_new_ids))

        # If the to read list was empty and is not anymore, fix the
        # header of the to read list
        if empty and len(self.waiting_list.list_id_articles) == 1:
            self.waiting_list.hideColumn(0)  # Hide id
            self.waiting_list.hideColumn(1)  # Hide percentage match
            self.waiting_list.hideColumn(2)  # Hide doi
            self.waiting_list.hideColumn(4)  # Hide date
            self.waiting_list.hideColumn(5)  # Hide journals
            self.waiting_list.hideColumn(6)  # Hide authors
            self.waiting_list.hideColumn(7)  # Hide abstracts
            self.waiting_list.hideColumn(9)  # Hide like
            self.waiting_list.hideColumn(10)  # Hide urls
            self.waiting_list.hideColumn(11)  # Hide new
            self.waiting_list.hideColumn(12)  # Hide topic_simple
            self.waiting_list.horizontalHeader().moveSection(8, 0)


    def emptyWait(self):

        """Method to empty the to-read list"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        self.waiting_list.list_id_articles = []
        self.waiting_list.list_new_ids = []

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
        except AttributeError:
            self.l.debug("updateView, AttributeError")
            self.model.setQuery(self.refineBaseQuery(table.base_query, table.topic_entries, table.author_entries))
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


    def cleanDb(self):

        """Slot to clean the database. Called from
        the window settings, but better to be here. Also
        deletes the unused pictures present in the
        graphical_abstracts folder"""

        mes = "You are about to clean your database, and you might loose data.\n\n\
If you do not know what you are doing, you should cancel now.\n\n\
If you click OK, the cleaning process will start"

        choice = QtGui.QMessageBox.critical(self, "Cleaning database", mes,
                                            QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Cancel)

        if choice == QtGui.QMessageBox.Cancel:
            return

        progress = QtGui.QProgressDialog("Deleting articles from unfollowed journals", None, 0, 100, self)
        progress.setWindowTitle("Cleaning database")
        progress.show()
        app.processEvents()

        query = QtSql.QSqlQuery(self.bdd)

        self.bdd.transaction()

        requete = "DELETE FROM papers WHERE journal NOT IN ("

        journals_to_care = self.getJournalsToCare()

        # Building the query
        for each_journal in self.getJournalsToCare():
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
        app.processEvents()


        query.exec_("DELETE FROM papers WHERE abstract=''")

        if not self.bdd.commit():
            self.l.critical("Problem while commiting, cleanDb")
        else:
            self.l.info("Removed incomplete articles from the database")

        progress.setLabelText("Deleting useless images")
        progress.setValue(40)
        app.processEvents()

        query.exec_("SELECT graphical_abstract FROM papers WHERE graphical_abstract != 'Empty'")

        images_path = []
        while query.next():
            images_path.append(query.record().value('graphical_abstract'))

        # images_path = [path for path in images_path if path != 'Empty']

        # Delete all the images which are not in the database (so not
        # corresponding to any article)
        for directory in os.walk(self.DATA_PATH + "/graphical_abstracts/"):
            for fichier in directory[2]:
                if fichier not in images_path:
                    os.remove(os.path.abspath(self.DATA_PATH + "/graphical_abstracts/{0}".format(fichier)))

        self.l.debug("Deleted all the useless images")

        progress.setLabelText("Building list of filtered articles")
        progress.setValue(60)
        app.processEvents()

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

        self.l.info("{} entries rejected will be deleted".format(len(articles_to_reject)))

        progress.setLabelText("Deleting filtered articles")
        progress.setValue(80)
        app.processEvents()

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

        # If the program is not in debug mod, exit the method
        if not self.debug_mod:
            progress.setValue(100)
            app.processEvents()
            progress.reset()
            return

        progress.setLabelText("Building list of filtered articles")
        progress.setValue(85)
        app.processEvents()

        # Build a list of DOIs to avoid duplicate in debug table
        list_doi = []
        query.exec_("SELECT doi FROM debug")
        while query.next():
            list_doi.append(query.record().value('doi'))

        progress.setLabelText("Inserting filtered articles in debug db")
        progress.setValue(90)
        app.processEvents()

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

        progress.setValue(100)
        app.processEvents()
        progress.reset()


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

            # if sys.platform=='win32':
            # if sys.platform in ['win32','cygwin','win64']:
                # os.startfile(url)
            # elif sys.platform=='darwin':
                # subprocess.Popen(['open', url])
            # else:
                # try:
                    # subprocess.Popen(['xdg-open', url])
                # except OSError:
                    # self.l.error("openInBrowser: Error. Please open a browser on {}".format(url))


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
            MyTwit(self, title, link, graphical_abstract)
        else:
            MyTwit(self, title, link)


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
        simple_title = functions.removeHtml(title) + " : spotted with chemBrows"

        # Conctsruct the body structure
        # body = "<span style='font-weight:bold'>{}</span></br> \
                # <span style='font-weight:bold'>Authors : </span>{}</br> \
                # <span style='font-weight:bold'>Journal : </span>{}</br></br> \
                # <span style='font-weight:bold'>Abstract : </span></br></br>{}</br></br> \
                # Click on this link to see the article on the editor's website: <a href=\"{}\">editor's website</a></br></br> \
                # This article was spotted with chemBrows.</br> Learn more about chemBrows : notre site web"

        body = "Click on this link to see the article on the editor's website: {}\n This article was spotted with chemBrows.\n Learn more about chemBrows : www.chembrows.com"
        body = body.format(link)

        url = "mailto:?subject={}&body={}"

        # if sys.platform=='win32':
        if sys.platform in ['win32', 'cygwin', 'win64']:
            webbrowser.open(url)

        elif sys.platform == 'darwin':
            url = url.format(simple_title, body)
            webbrowser.open(url)
            # subprocess.Popen(['open', url])

        else:
            # Create an url to be opened with a mail client
            body = urllib.parse.quote(body)
            url = url.format(simple_title, body)
            webbrowser.open(url)
            # try:
                # subprocess.Popen(['xdg-email', url])
            # except OSError:
                # self.l.error("shareByEmail: OSError")



    def calculatePercentageMatch(self, update=False):

        """Slot to calculate the match percentage.
        If update= False, does not update the view"""

        self.model.submitAll()

        self.predictor = Predictor(self.l, self.bdd)

        mes = "ChemBrows does not have enough data to calculate the Hot paperness yet.\n\n"
        mes += "Feed it more !"

        # Display a message if the classifier is not trained yet
        if self.predictor.initializePipeline() is None and update:
            QtGui.QMessageBox.information(self, "Feed ChemBrows", mes,
                                          QtGui.QMessageBox.Ok)

            # Re-sort otherwise the display looks messy
            self.searchByButton()
            return

        def whenDone():
            mes = "ChemBrows does not have enough data to calculate the Hot paperness yet.\n\n"
            mes += "Feed it more !"

            self.progress.reset()

            # Display a message if the classifier is not trained yet
            if not self.predictor.calculated_something:
                QtGui.QMessageBox.information(self, "Feed ChemBrows", mes,
                                              QtGui.QMessageBox.Ok)
                app.processEvents()

            self.list_tables_in_tabs[0].verticalScrollBar().setSliderPosition(0)

            del self.predictor

            if update:
                self.searchByButton()
            else:
                mes = "{} new articles were added to your database !"
                mes = mes.format(self.counter)
                QtGui.QMessageBox.information(self, "New articles", mes,
                                              QtGui.QMessageBox.Ok)

            self.parsing = False

        self.parsing = True

        # https://contingencycoder.wordpress.com/2013/08/04/quick-tip-qprogressbar-as-a-busy-indicator/
        # If the range is set to 0, get a busy progress bar,
        # without percentage
        app.processEvents()
        self.progress = QtGui.QProgressDialog("Calculating Hot Paperness...", None, 0, 0, self)
        self.progress.setWindowTitle("Hot Paperness calculation")
        self.progress.show()
        app.processEvents()

        self.predictor.finished.connect(whenDone)
        self.predictor.start()



    def toggleLike(self):

        """Slot to mark a post liked"""

        table = self.list_tables_in_tabs[self.onglets.currentIndex()]

        like = table.model().index(table.selectionModel().currentIndex().row(), 9).data()
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

        # self.setGeometry(0, 25, 1900 , 1020)
        # self.showMaximized()
        self.setWindowTitle('ChemBrows')

        # ------------------------- BUILDING THE MENUS -------------------------------------------------------------

        self.menubar = self.menuBar()

        # Building files menu
        self.fileMenu = self.menubar.addMenu('&Files')
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addAction(self.exitAction)

        # Building edition menu
        # self.editMenu = self.menubar.addMenu("&Edition")
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

        self.helpMenu = self.menubar.addMenu("&Help")
        self.helpMenu.addAction(self.tutoAction)
        self.helpMenu.addAction(self.showAboutAction)

        # # ------------------------- TOOLBAR  -----------------------------------------------

        # On ajoute une toolbar en la nommant pr l'indentifier,
        # Puis on ajoute les widgets
        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.setMovable(False)

        # Refresh button. I use buttons and not actions because I want to
        # set their style
        self.button_refresh = QtGui.QPushButton()
        self.button_refresh.setIcon(QtGui.QIcon("./images/refresh.png"))
        self.button_refresh.setIconSize(QtCore.QSize(36, 36))
        self.button_refresh.setToolTip("Refresh: download new posts")
        self.button_refresh.setAccessibleName('toolbar_round_button')

        # Percentage calculation button
        self.button_calculate_percentage = QtGui.QPushButton()
        self.button_calculate_percentage.setIcon(QtGui.QIcon("./images/stats.png"))
        self.button_calculate_percentage.setIconSize(QtCore.QSize(36, 36))
        self.button_calculate_percentage.setToolTip("Re-calculate Hot Paperness")
        self.button_calculate_percentage.setAccessibleName('toolbar_round_button')

        # Button to display new articles, or view them all
        self.button_search_new = QtGui.QPushButton('View unread')
        self.button_search_new.setToolTip("Display unread articles")
        self.button_search_new.setAccessibleName('toolbar_button')

        # Button to change the sorting method of the articles
        self.button_sort_by = QtGui.QPushButton()
        self.button_sort_by.setToolTip("Sort articles by date or Hot Paperness")
        self.button_sort_by.clicked.connect(lambda: self.changeSortingMethod(None, self.sortingReversedAction.isChecked()))
        self.button_sort_by.setAccessibleName('toolbar_button')

        # Create a research bar and set its size
        self.line_research = ButtonLineEdit('images/glyphicons_197_remove', self)
        self.line_research.setToolTip("Quick search")
        self.line_research.setPlaceholderText("Quick search")
        self.line_research.setFixedSize(self.line_research.sizeHint().width(), self.line_research.sizeHint().height() * 1.3)

        # Advanced search button
        self.button_advanced_search = QtGui.QPushButton()
        self.button_advanced_search.setIcon(QtGui.QIcon("./images/advanced_search.png"))
        self.button_advanced_search.setIconSize(QtCore.QSize(36, 36))
        self.button_advanced_search.setToolTip("Advanced search: more powerful research")
        self.button_advanced_search.setAccessibleName('toolbar_round_button')

        self.button_settings = QtGui.QPushButton()
        self.button_settings.setIcon(QtGui.QIcon("./images/settings.png"))
        self.button_settings.setIconSize(QtCore.QSize(36, 36))
        self.button_settings.setToolTip("Preferences, settings")
        self.button_settings.setAccessibleName('toolbar_round_button')

        # Empty widget acting like a spacer
        self.empty_widget = QtGui.QWidget()
        self.empty_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred);

        self.toolbar.addWidget(self.button_refresh)
        self.toolbar.addWidget(self.button_calculate_percentage)
        # self.toolbar.addSeparator()
        self.toolbar.addWidget(self.button_search_new)
        self.toolbar.addWidget(self.button_sort_by)
        # self.toolbar.addSeparator()
        self.toolbar.addWidget(self.line_research)
        self.toolbar.addWidget(self.button_advanced_search)
        self.toolbar.addWidget(self.empty_widget)
        self.toolbar.addWidget(self.button_settings)

        # Create a button to reset everything
        # self.button_back = QtGui.QPushButton(QtGui.QIcon('images/glyphicons_170_step_backward'), 'Back')
        # self.button_view_all = QtGui.QPushButton('View all')
        # self.toolbar.addWidget(self.button_view_all)




        # ------------------------- LEFT AREA --------------------------------

        # Create scrollarea to put the journals buttons
        self.scroll_tags = QtGui.QScrollArea()

        # Create scrolling zone
        # http://www.mattmurrayanimation.com/archives/tag/how-do-i-use-a-qscrollarea-in-pyqt
        self.scrolling_tags = QtGui.QWidget()

        self.vbox_all_tags = QtGui.QVBoxLayout()
        self.scrolling_tags.setLayout(self.vbox_all_tags)

        self.scroll_tags.hide()

        # ------------------------- RIGHT TOP AREA ---------------------------

        # Creation of a gridLayout to handle the top right area
        self.area_right_top = QtGui.QWidget()
        self.grid_area_right_top = QtGui.QGridLayout()
        self.grid_area_right_top.setContentsMargins(0, 0, 0, 0)
        self.area_right_top.setLayout(self.grid_area_right_top)

        # Here I set a prelabel: a label w/ just "Title: " to label the title.
        # I set the sizePolicy of this prelabel to the minimum. It will stretch to
        # the minimum. Makes the display better with the grid
        prelabel_title = QtGui.QLabel("Title: ")
        prelabel_title.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_title = QtGui.QLabel()
        self.label_title.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_title.setWordWrap(True)
        self.label_title.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        prelabel_author = QtGui.QLabel("Author(s): ")
        prelabel_author.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_author = QtGui.QLabel()
        self.label_author.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_author.setWordWrap(True)
        self.label_author.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        prelabel_journal = QtGui.QLabel("Journal: ")
        prelabel_journal.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_journal = QtGui.QLabel()
        self.label_journal.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_journal.setWordWrap(True)
        self.label_journal.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        prelabel_date = QtGui.QLabel("Date: ")
        prelabel_date.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.label_date = QtGui.QLabel()
        self.label_date.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_date.setWordWrap(True)
        self.label_date.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        # Buttons for the display of the article: zoom & dark background
        self.button_zoom_less = QtGui.QPushButton()
        self.button_zoom_less.setIcon(QtGui.QIcon('./images/zoom_out.png'))
        self.button_zoom_less.setIconSize(QtCore.QSize(30, 30))
        self.button_zoom_less.hide()
        self.button_zoom_more = QtGui.QPushButton()
        self.button_zoom_more.setIcon(QtGui.QIcon('./images/zoom_in.png'))
        self.button_zoom_more.setIconSize(QtCore.QSize(30, 30))
        self.button_zoom_more.hide()
        self.button_color_read = QtGui.QPushButton()
        self.button_color_read.setIcon(QtGui.QIcon('./images/black_text.png'))
        self.button_color_read.setIconSize(QtCore.QSize(30, 30))
        self.button_color_read.hide()

        # Button to share on twitter
        self.button_twitter = QtGui.QPushButton()
        self.button_twitter.setIcon(QtGui.QIcon('./images/twitter.png'))
        self.button_twitter.setIconSize(QtCore.QSize(30, 30))
        self.button_twitter.hide()

        # Button to share by email
        self.button_share_mail = QtGui.QPushButton()
        self.button_share_mail.setIcon(QtGui.QIcon('./images/email.png'))
        self.button_share_mail.setIconSize(QtCore.QSize(30, 30))
        self.button_share_mail.hide()

        # A QWebView to render the sometimes rich text of the abstracts
        self.text_abstract = WebViewPerso(self)

        # Building the grid
        self.grid_area_right_top.addWidget(prelabel_title, 0, 0, 1, 4)
        self.grid_area_right_top.addWidget(self.label_title, 0, 1)
        self.grid_area_right_top.addWidget(prelabel_author, 1, 0)
        self.grid_area_right_top.addWidget(self.label_author, 1, 1, 1, 4)
        self.grid_area_right_top.addWidget(prelabel_journal, 2, 0)
        self.grid_area_right_top.addWidget(self.label_journal, 2, 1, 1, 4)
        self.grid_area_right_top.addWidget(prelabel_date, 3, 0)
        self.grid_area_right_top.addWidget(self.label_date, 3, 1, 1, 4)

        # An empty widget, acts as spacer
        self.empty_widget = QtGui.QWidget()
        self.empty_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred);

        # A HBoxLayout to store the article "toolbar"
        self.hbox_toolbar_article = QtGui.QHBoxLayout()
        self.hbox_toolbar_article.addWidget(self.button_zoom_less, alignment=QtCore.Qt.AlignLeft)
        self.hbox_toolbar_article.addWidget(self.button_zoom_more, alignment=QtCore.Qt.AlignLeft)
        self.hbox_toolbar_article.addWidget(self.button_color_read, alignment=QtCore.Qt.AlignLeft)
        self.hbox_toolbar_article.addWidget(self.empty_widget)
        self.hbox_toolbar_article.addWidget(self.button_twitter, alignment=QtCore.Qt.AlignRight)
        self.hbox_toolbar_article.addWidget(self.button_share_mail, alignment=QtCore.Qt.AlignRight)

        self.grid_area_right_top.addLayout(self.hbox_toolbar_article, 4, 0, 1, 4)
        self.grid_area_right_top.addWidget(self.text_abstract, 5, 0, 1, 4)

        # USEFULL: set the size of the grid and its widgets to the minimum
        self.grid_area_right_top.setRowStretch(5, 1)

        # ------------------------- ASSEMBLING THE AREAS ----------------------

        # Main part of the window in a tab.
        # Allows to create other tabs
        self.onglets = TabPerso(self)
        # self.onglets.setContentsMargins(0, 0, 0, 0)

        self.central_widget = QtGui.QWidget()
        self.hbox_central = QtGui.QHBoxLayout()
        self.central_widget.setLayout(self.hbox_central)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter2.addWidget(self.onglets)
        self.splitter2.addWidget(self.area_right_top)

        self.hbox_central.addWidget(self.scroll_tags)
        self.hbox_central.addWidget(self.splitter2)

        # Create the main table, at index 0
        self.createSearchTab("All articles", "SELECT * FROM papers")

        self.setCentralWidget(self.central_widget)

        with open("./config/styles/style.css", "r") as fh:
            style = fh.read()
            self.central_widget.setStyleSheet(style)
            self.toolbar.setStyleSheet(style)

        with open("./config/styles/toolbar.css", "r") as fh:
            style = fh.read()
            self.scroll_tags.setStyleSheet(style)
            self.button_search_new.setStyleSheet(style)
            self.button_sort_by.setStyleSheet(style)
            self.line_research.setStyleSheet(style)

        with open("./config/styles/buttons.css", "r") as fh:
            style = fh.read()
            self.button_twitter.setStyleSheet(style)
            self.button_share_mail.setStyleSheet(style)
            self.button_zoom_less.setStyleSheet(style)
            self.button_zoom_more.setStyleSheet(style)
            self.button_color_read.setStyleSheet(style)
            self.button_refresh.setStyleSheet(style)
            self.button_calculate_percentage.setStyleSheet(style)
            self.button_advanced_search.setStyleSheet(style)
            self.button_settings.setStyleSheet(style)


if __name__ == '__main__':
    # logger = MyLog()
    # try:
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('./images/icon_main.png'))
    # ex = Fenetre(logger)
    ex = Fenetre()
    app.processEvents()
    sys.exit(app.exec_())

    # except Exception as e:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # exc_type = type(e).__name__
        # fname = exc_tb.tb_frame.f_code.co_filename
        # logger.warning("File {0}, line {1}".format(fname, exc_tb.tb_lineno))
        # logger.warning("{0}: {1}".format(exc_type, e))
    # finally:
        # # Try to kill all the threads
    # try:
        # for worker in ex.list_threads:
            # worker.terminate()

            # logger.debug("Starting killing the futures")
            # to_cancel = worker.list_futures_urls + worker.list_futures_images
            # for future in to_cancel:
                # if type(future) is not bool:
                    # future.cancel()
            # logger.debug("Done killing the futures")

        # logger.info("Quitting the program, killing all the threads")
    # except AttributeError:
        # logger.info("Quitting the program, no threads")
