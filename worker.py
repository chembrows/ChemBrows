#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore
import feedparser
#import datetime

import hosts
import functions


class Worker(QtCore.QThread):

    """Subclassing the class in order to provide a thread.
    The thread is used to parse the RSS flux, in background. The
    main UI remains functional"""

    #http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
    #https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots


    def __init__(self, url_feed, logger):

        QtCore.QThread.__init__(self)

        self.exiting = False
        self.url_feed = url_feed
        self.l = logger
        self.l.debug("Starting parsing of the new articles")
        self.start()


    def __del__(self):

        """Method to destroy the thread properly"""
    
        self.exiting = True
        self.wait()


    def run(self):

        """Main function. Starts the real business"""

        #Get the RSS page of the url provided
        feed = feedparser.parse(self.url_feed)

        #Get the journal name
        journal = feed['feed']['title']

        self.l.debug("{0}: {1}".format(journal, len(feed.entries)))

        i = 0

        for entry in feed.entries:

            #Get the DOI, a unique number for a publication
            doi = hosts.getDoi(journal, entry)
            list_doi = functions.listDoi()

            if doi in list_doi:
                self.l.debug("Post already in db")
                continue

            title, journal_abb, date, authors, abstract, graphical_abstract, url = hosts.getData(journal, entry)

            query = QtSql.QSqlQuery("fichiers.sqlite")

            query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url) VALUES(?, ?, ?, ?, ?, ?, ?, ?)")

            params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url)

            for value in params:
                query.addBindValue(value)

            retour = query.exec_()

            #If the query went wrong, print the details
            if not retour:
                self.l.error(query.lastError().text())
                self.l.debug(query.lastQuery())
            else:
                i += 1
                self.l.debug(i)
                self.l.debug("{1} Adding {0} to the database".format(title, journal))

        self.l.info("{0}: {1} entries added".format(journal, i))


if __name__ == "__main__":

    worker = Worker()
    worker.render("ang.xml")

    pass

