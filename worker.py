#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore
import feedparser

import hosts


class Worker(QtCore.QThread):

    """Subclassing the class in order to provide a thread.
    The thread is used to parse the RSS flux, in background. The
    main UI remains functional"""

    # http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
    # https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots


    def __init__(self, url_feed, logger, bdd):

        QtCore.QThread.__init__(self)

        self.exiting = False
        self.url_feed = url_feed
        self.l = logger
        self.bdd = bdd
        self.l.debug("Starting parsing of the new articles")
        self.start()


    def __del__(self):

        """Method to destroy the thread properly"""

        self.exiting = True
        self.wait()


    def run(self):

        """Main function. Starts the real business"""

        # Get the RSS page of the url provided
        feed = feedparser.parse(self.url_feed)

        # Get the journal name
        journal = feed['feed']['title']

        self.l.debug("{0}: {1}".format(journal, len(feed.entries)))

        # Prepare the queries here, only once
        query1 = QtSql.QSqlQuery("fichiers.sqlite")
        query1.prepare("UPDATE papers SET title= ?, authors=?, abstract=?, graphical_abstract=?, verif=?, new=?, topic_simple=? WHERE doi=?")
        query2 = QtSql.QSqlQuery("fichiers.sqlite")
        query2.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url, verif, new, topic_simple)\
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

        self.bdd.transaction()

        for entry in feed.entries:

            # Get the DOI, a unique number for a publication
            doi = hosts.getDoi(journal, entry)
            list_doi, list_ok = self.listDoi()

            if doi in list_doi:

                # If the article is in db, with all the data, continue
                if list_ok[list_doi.index(doi)]:
                    self.l.debug("Post already in db and ok")
                    continue
                else:
                    title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry)

                    self.l.debug("Updating post {0}".format(journal))

                    # Checking if the data are complete
                    if type(abstract) is not str or type(graphical_abstract) is not str or type(authors) is not str:
                        verif = 0
                    else:
                        verif = 1

                    # On met new à 1 et non pas à True
                    params = (title, authors, abstract, graphical_abstract, verif, 1, topic_simple, doi)

                    for value in params:
                        query1.addBindValue(value)

                    retour = query1.exec_()

                    # If the query went wrong, print the details
                    if not retour:
                        self.l.error(query1.lastError().text())
                        self.l.debug(query1.lastQuery())
                    else:
                        self.l.debug("{1} Corrected {0} in the database".format(title, journal))
            else:

                title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry)


                # Checking if the data are complete
                if type(abstract) is not str or type(graphical_abstract) is not str:
                    verif = 0
                else:
                    verif = 1

                # On met new à 1 et pas à true
                params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url, verif, 1, topic_simple)

                for value in params:
                    query2.addBindValue(value)

                retour = query2.exec_()

                # If the query went wrong, print the details
                if not retour:
                    self.l.error(query2.lastError().text())
                    self.l.debug(query2.lastQuery())
                else:
                    self.l.debug("Adding {0} to the database".format(title))

        # self.l.info("{0}: {1} entries added".format(journal, i))
        if self.bdd.commit():
            self.l.debug("Treatment of new entries done")



    def listDoi(self):

        """Function to get the doi from the database.
        Also returns a list of booleans to check if the data are complete"""

        list_doi = []
        list_ok = []

        query = QtSql.QSqlQuery("fichiers.sqlite")
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



if __name__ == "__main__":

    worker = Worker()
    worker.render("ang.xml")

    pass
