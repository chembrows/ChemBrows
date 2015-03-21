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


    def __init__(self, url_feed, logger, bdd):

        QtCore.QThread.__init__(self)

        self.l = logger
        self.bdd = bdd

        # Define a path attribute to easily change it
        # for the tests
        self.path = "./graphical_abstracts/"

        # DEBUG
        self.url_feed = url_feed

        self.l.info("Starting parsing of the new articles")

        # List to store the urls of the pages to request
        self.list_futures_urls = []
        self.list_futures_images = []

        # self.start()


    def __del__(self):

        """Method to destroy the thread properly"""

        self.wait()


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
        self.list_doi, self.list_ok = self.listDoi()
        # self.session_images = FuturesSession(max_workers=len(self.feed))
        # self.session_images = FuturesSession(max_workers=5)
        self.session_images = FuturesSession(max_workers=10)

        # Load the journals
        rsc = hosts.getJournals("rsc")[0]
        acs = hosts.getJournals("acs")[0]
        wiley = hosts.getJournals("wiley")[0]
        npg = hosts.getJournals("npg")[0]
        science = hosts.getJournals("science")[0]
        nas = hosts.getJournals("nas")[0]
        elsevier = hosts.getJournals("elsevier")[0]
        thieme = hosts.getJournals("thieme")[0]
        beil = hosts.getJournals("beilstein")[0]

        query = QtSql.QSqlQuery(self.bdd)

        self.bdd.transaction()

        # The feeds of these journals are complete
        # if journal in wiley + science + elsevier:
        if journal in science + elsevier + beil:

            self.list_futures_urls = [True] * len(self.feed.entries)

            for entry in self.feed.entries:

                # Get the DOI, a unique number for a publication
                doi = hosts.getDoi(journal, entry)

                if doi in self.list_doi and self.list_ok[self.list_doi.index(doi)]:
                    self.list_futures_images.append(True)
                    self.l.info("Skipping")
                    continue
                else:
                    title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry)

                    # Checking if the data are complete
                    # TODO: normally fot these journals, no need to check
                    if type(abstract) is not str:
                        verif = 0
                    else:
                        verif = 1

                    if doi in self.list_doi and doi not in self.list_ok:
                        query.prepare("UPDATE papers SET title=?, date=?, authors=?, abstract=?, verif=?, topic_simple=? WHERE doi=?")
                        params = (title, date, authors, abstract, verif, topic_simple, doi)
                        self.l.info("Updating {0} in the database".format(doi))
                    else:
                        query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new, topic_simple)\
                                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
                        # Set new to 1 and not to true
                        params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1, topic_simple)
                        self.l.info("Adding {0} to the database".format(doi))

                    for value in params:
                        query.addBindValue(value)


                    query.exec_()

                    if graphical_abstract == "Empty":
                        self.list_futures_images.append(True)
                    else:
                        # Use a user-agent browser, some journals block bots
                        headers = {'User-agent': 'Mozilla/5.0'}
                        headers["Referer"] = url

                        future_image = self.session_images.get(graphical_abstract, headers=headers, timeout=20)
                        self.list_futures_images.append(future_image)
                        future_image.add_done_callback(functools.partial(self.pictureDownloaded, doi))

        else:
            # session = FuturesSession(max_workers=len(self.feed.entries))
            # session = FuturesSession(max_workers=5)
            session = FuturesSession(max_workers=10)

            for entry in self.feed.entries:

                doi = hosts.getDoi(journal, entry)

                if doi in self.list_doi and self.list_ok[self.list_doi.index(doi)]:
                    self.list_futures_urls.append(True)
                    self.list_futures_images.append(True)
                    self.l.info("Skipping")
                    continue
                else:
                    try:
                        url = entry.feedburner_origlink
                    except AttributeError:
                        url = entry.link

                    future = session.get(url, timeout=20)
                    self.list_futures_urls.append(future)
                    future.add_done_callback(functools.partial(self.completeData, doi, journal, entry))

        while not self.checkFuturesRunning():
            # self.wait()
            self.sleep(3)
            # pass

        if not self.bdd.commit():
            self.l.error(self.bdd.lastError().text())
            self.l.error("Problem when comitting data for {}".format(journal))

        self.l.info("Exiting thread for {}".format(journal))


    def completeData(self, doi, journal, entry, future):

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

        title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry, response)

        # Checking if the data are complete
        if type(abstract) is not str or type(authors) is not str:
            verif = 0
        else:
            verif = 1

        if doi in self.list_doi and doi not in self.list_ok:
            query.prepare("UPDATE papers SET title=?, date=?, authors=?, abstract=?, verif=?, topic_simple=? WHERE doi=?")
            params = (title, date, authors, abstract, verif, topic_simple, doi)
            self.l.info("Updating {0} in the database".format(doi))
        else:
            query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new, topic_simple)\
                           VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1, topic_simple)
            self.l.info("Adding {0} to the database".format(doi))

        for value in params:
            query.addBindValue(value)

        query.exec_()

        if graphical_abstract == "Empty":
            self.list_futures_images.append(True)
        else:
            headers = {'User-agent': 'Mozilla/5.0'}
            headers["Referer"] = url

            future_image = self.session_images.get(graphical_abstract, headers=headers, timeout=20)
            self.list_futures_images.append(future_image)
            future_image.add_done_callback(functools.partial(self.pictureDownloaded, doi))



    def pictureDownloaded(self, doi, future):

        try:
            response = future.result()
        except requests.exceptions.ReadTimeout:
            self.l.error("ReadTimeout for image")
            self.list_futures_images.append(True)
            return
        except requests.exceptions.ConnectionError:
            self.l.error("ConnectionError for image")
            self.list_futures_images.append(True)
            return
        except requests.exceptions.MissingSchema:
            pass

        query = QtSql.QSqlQuery(self.bdd)

        if response.status_code == requests.codes.ok:

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


    def checkFuturesRunning(self):

        total_futures = self.list_futures_images + self.list_futures_urls
        states_futures = []

        for result in total_futures:
            if type(result) == bool:
                states_futures.append(result)
            else:
                states_futures.append(result.done())

        if False not in states_futures and len(total_futures) == len(self.feed.entries) * 2:
            return True
        else:
            return False


    def listDoi(self):

        """Function to get the doi from the database.
        Also returns a list of booleans to check if the data are complete"""

        list_doi = []
        list_ok = []

        query = QtSql.QSqlQuery(self.bdd)
        query.exec_("SELECT * FROM papers")

        while query.next():
            record = query.record()
            list_doi.append(record.value('doi'))

            if record.value('verif') == 1 and record.value('graphical_abstract') != "Empty":
                # Try to download the images again if it didn't work before
                list_ok.append(True)
            else:
                list_ok.append(False)

        return list_doi, list_ok
