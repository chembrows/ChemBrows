#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore
import feedparser
import functools
from requests_futures.sessions import FuturesSession
import requests
from io import open as iopen

import hosts
import functions


class Worker(QtCore.QThread):

    """Subclassing the class in order to provide a thread.
    The thread is used to parse the RSS flux, in background. The
    main UI remains functional"""

    # http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
    # https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots


    def __init__(self, logger, bdd):

        QtCore.QThread.__init__(self)

        self.l = logger
        self.bdd = bdd

        # Define a path attribute to easily change it
        # for the tests
        self.path = "./graphical_abstracts/"

        # self.l.info("Starting parsing of the new articles")

        # List to store the urls of the pages to request
        self.list_futures_urls = []
        self.list_futures_images = []

        # self.start()

    def setUrl(self, url_feed):

        self.url_feed = url_feed


    def __del__(self):

        """Method to destroy the thread properly"""

        self.wait()
        self.exit()


    def run(self):

        """Main function. Starts the real business"""

        # Get the RSS page of the url provided
        self.feed = feedparser.parse(self.url_feed)

        # Get the journal name
        try:
            journal = self.feed['feed']['title']
        except KeyError:
            self.l.error("No title for the journal ! Aborting")
            self.l.error(self.url_feed)
            return

        self.l.info("{0}: {1}".format(journal, len(self.feed.entries)))

        # Lists to check if the post is in the db, and if
        # it has all the infos
        # self.session_images = FuturesSession(max_workers=10)
        # self.session_images = FuturesSession(max_workers=20)
        self.session_images = FuturesSession(max_workers=40)

        rsc, rsc_abb, _ = hosts.getJournals("rsc")
        acs, acs_abb, _ = hosts.getJournals("acs")
        wiley, wiley_abb, _ = hosts.getJournals("wiley")
        npg, npg_abb, _ = hosts.getJournals("npg")
        science, science_abb, _ = hosts.getJournals("science")
        nas, nas_abb, _ = hosts.getJournals("nas")
        elsevier, elsevier_abb, _ = hosts.getJournals("elsevier")
        thieme, thieme_abb, _ = hosts.getJournals("thieme")
        beil, beil_abb, _ = hosts.getJournals("beilstein")

        total_journals = rsc + acs + wiley + npg + science + \
                         nas + elsevier + thieme + beil

        total_abb = rsc_abb + acs_abb + wiley_abb + npg_abb + science_abb + \
                    nas_abb + elsevier_abb + thieme_abb + beil_abb

        journal_abb = total_abb[total_journals.index(journal)]

        self.list_doi, self.list_ok = self.listDoi(journal_abb)

        # Get the company as a simple string
        if journal in rsc:
            company = 'rsc'
        elif journal in acs:
            company = 'acs'
        elif journal in wiley:
            company = 'wiley'
        elif journal in npg:
            company = 'npg'
        elif journal in science:
            company = 'science'
        elif journal in nas:
            company = 'nas'
        elif journal in elsevier:
            company = 'elsevier'
        elif journal in thieme:
            company = 'thieme'
        elif journal in beil:
            company = 'beil'

        query = QtSql.QSqlQuery(self.bdd)
        self.bdd.transaction()

        # The feeds of these journals are complete
        # if journal in wiley + science + elsevier:
        if journal in science + elsevier + beil:

            self.list_futures_urls = [True] * len(self.feed.entries)

            for entry in self.feed.entries:

                # Get the DOI, a unique number for a publication
                doi = hosts.getDoi(company, journal, entry)

                if doi in self.list_doi and self.list_ok[self.list_doi.index(doi)]:
                    self.list_futures_images.append(True)
                    self.l.debug("Skipping")
                    continue
                else:
                    title, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(company, journal, entry)

                    # Checking if the data are complete
                    # TODO: normally fot these journals, no need to check
                    if type(abstract) is not str:
                        verif = 0
                    else:
                        verif = 1

                    if doi in self.list_doi and doi not in self.list_ok:
                        query.prepare("UPDATE papers SET title=?, date=?, authors=?, abstract=?, verif=?, topic_simple=? WHERE doi=?")
                        params = (title, date, authors, abstract, verif, topic_simple, doi)
                        self.l.debug("Updating {0} in the database".format(doi))
                    else:
                        query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new, topic_simple)\
                                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
                        # Set new to 1 and not to true
                        params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1, topic_simple)
                        self.l.debug("Adding {0} to the database".format(doi))

                    for value in params:
                        query.addBindValue(value)

                    query.exec_()

                    if graphical_abstract == "Empty":
                        self.list_futures_images.append(True)
                    else:
                        # Use a user-agent browser, some journals block bots
                        headers = {'User-agent': 'Mozilla/5.0'}
                        headers["Referer"] = url

                        future_image = self.session_images.get(graphical_abstract, headers=headers, timeout=10)
                        self.list_futures_images.append(future_image)
                        future_image.add_done_callback(functools.partial(self.pictureDownloaded, doi, url))

        else:
            # session = FuturesSession(max_workers=10)
            # session = FuturesSession(max_workers=20)
            session = FuturesSession(max_workers=40)

            for entry in self.feed.entries:

                doi = hosts.getDoi(company, journal, entry)

                if doi in self.list_doi and self.list_ok[self.list_doi.index(doi)]:
                    self.list_futures_urls.append(True)
                    self.list_futures_images.append(True)
                    self.l.debug("Skipping")
                    continue
                else:
                    try:
                        url = entry.feedburner_origlink
                    except AttributeError:
                        url = entry.link

                    future = session.get(url, timeout=10)
                    self.list_futures_urls.append(future)
                    future.add_done_callback(functools.partial(self.completeData, doi, company, journal, journal_abb, entry))

        while not self.checkFuturesRunning(company):
            # self.wait()
            # self.sleep(2)
            self.sleep(0.2)

        if not self.bdd.commit():
            self.l.error(self.bdd.lastError().text())
            self.l.error("Problem when comitting data for {}".format(journal))

        self.l.info("Exiting thread for {}".format(journal))


    def completeData(self, doi, company, journal, journal_abb, entry, future):

        """Callback to handle the response of the futures trying to
        download the page of the articles"""

        try:
            response = future.result()
        except requests.exceptions.ReadTimeout:
            self.l.error("ReadTimeout for {}".format(journal))
            self.list_futures_images.append(True)
            return
        except requests.exceptions.ConnectionError:
            self.l.error("ConnectionError for {}".format(journal))
            self.list_futures_images.append(True)
            return

        query = QtSql.QSqlQuery(self.bdd)

        try:
            title, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(company, journal, entry, response)
        except TypeError:
            self.l.error("getData returned None for {}".format(journal))
            self.list_futures_images.append(True)
            return

        # Checking if the data are complete
        if type(abstract) is not str or type(authors) is not str:
            verif = 0
        else:
            verif = 1

        if doi in self.list_doi and doi not in self.list_ok:
            query.prepare("UPDATE papers SET title=?, date=?, authors=?, abstract=?, verif=?, topic_simple=? WHERE doi=?")
            params = (title, date, authors, abstract, verif, topic_simple, doi)
            self.l.debug("Updating {0} in the database".format(doi))
        else:
            query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new, topic_simple)\
                           VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1, topic_simple)
            self.l.debug("Adding {0} to the database".format(doi))

        for value in params:
            query.addBindValue(value)

        query.exec_()

        if graphical_abstract == "Empty":
            self.list_futures_images.append(True)
        else:
            headers = {'User-agent': 'Mozilla/5.0'}
            headers["Referer"] = url

            future_image = self.session_images.get(graphical_abstract, headers=headers, timeout=10)
            self.list_futures_images.append(future_image)
            future_image.add_done_callback(functools.partial(self.pictureDownloaded, doi, url))


    def pictureDownloaded(self, doi, entry_url, future):

        """Callback to handle the response of the futures
        downloading a picture"""

        try:
            response = future.result()
        except requests.exceptions.ReadTimeout:
            self.l.error("ReadTimeout for image: {}".format(entry_url))
            return
        except requests.exceptions.ConnectionError:
            self.l.error("ConnectionError for image: {}".format(entry_url))
            return
        except requests.exceptions.MissingSchema:
            self.l.error("MissingSchema for image: {}".format(entry_url))
            return

        query = QtSql.QSqlQuery(self.bdd)

        if response.status_code is requests.codes.ok:

            path = self.path

            # Save the page
            with iopen(path + functions.simpleChar(response.url), 'wb') as file:
                file.write(response.content)
                self.l.debug("Image ok")

            query.prepare("UPDATE papers SET graphical_abstract=? WHERE doi=?")

            graphical_abstract = functions.simpleChar(response.url)

            params = (graphical_abstract, doi)

        else:
            self.l.debug("Bad return code: {}".format(response.status_code))
            graphical_abstract = "Empty"
            verif = 0

            query.prepare("UPDATE papers SET graphical_abstract=?, verif=? WHERE doi=?")

            params = (graphical_abstract, verif, doi)

        for value in params:
            query.addBindValue(value)

        query.exec_()


<<<<<<< HEAD
=======
    # @profile
    def checkFuturesRunning(self, company):

        """Method to check if some futures are still running.
        Returns True if all the futures are done"""
>>>>>>> memory

        total_futures = self.list_futures_images + self.list_futures_urls
        states_futures = []

        for result in total_futures:
            if type(result) is bool:
                states_futures.append(result)
            else:
                states_futures.append(result.done())

        if False not in states_futures and len(total_futures) == len(self.feed.entries) * 2:
            return True
        else:
            return False


    def listDoi(self, journal_abb):

        """Function to get the doi from the database.
        Also returns a list of booleans to check if the data are complete"""

        list_doi = []
        list_ok = []

        query = QtSql.QSqlQuery(self.bdd)
        query.prepare("SELECT * FROM papers WHERE journal=?")
        query.addBindValue(journal_abb)
        query.exec_()

        while query.next():
            record = query.record()
            list_doi.append(record.value('doi'))

            if record.value('verif') == 1 and record.value('graphical_abstract') != "Empty":
                # Try to download the images again if it didn't work before
                list_ok.append(True)
            else:
                list_ok.append(False)

        return list_doi, list_ok
