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

        query = QtSql.QSqlQuery("fichiers.sqlite")

        i = 0

        for entry in feed.entries:

            #Get the DOI, a unique number for a publication
            doi = hosts.getDoi(journal, entry)
            list_doi, list_ok = functions.listDoi()

            if doi in list_doi:
                self.l.debug("Post already in db")

                #If the article is in db, with all the data, continue
                if list_ok[list_doi.index(doi)]:
                    continue
                else:
                    title, journal_abb, date, authors, abstract, graphical_abstract, url = hosts.getData(journal, entry)
                    query.prepare("UPDATE papers SET title= ?, authors=?, abstract=?, graphical_abstract=?, verif=?, new=? WHERE doi=?")

                    #Checking if the data are complete
                    if type(abstract) is not str or type(graphical_abstract) is not str or type(authors) is not str:
                        verif = 0
                    else:
                        verif = 1

                    #On met new à 1 et non pas à True
                    params = (title, authors, abstract, graphical_abstract, verif, 1, doi)

                    for value in params:
                        query.addBindValue(value)

                    retour = query.exec_()

                    #If the query went wrong, print the details
                    if not retour:
                        self.l.error(query.lastError().text())
                        self.l.debug(query.lastQuery())
                    else:
                        self.l.debug(i)
                        self.l.debug("{1} Corrected {0} in the database".format(title, journal))
            else:

                title, journal_abb, date, authors, abstract, graphical_abstract, url = hosts.getData(journal, entry)

                query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new)\
                               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

                #Checking if the data are complete
                if type(abstract) is not str or type(graphical_abstract) is not str:
                    verif = 0
                else:
                    verif = 1

                #On met new à 1 et pas à true
                params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1)

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
                    #self.l.debug("{1} Adding {0} to the database".format(title, journal))

        #self.l.info("{0}: {1} entries added".format(journal, i))


if __name__ == "__main__":

    worker = Worker()
    worker.render("ang.xml")

    pass

