#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import datetime
import feedparser
from PyQt4 import QtSql
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

#Personal modules
from log import MyLog
import hosts


#l = MyLog(total=True)
#l.setLevel(logging.DEBUG)

#bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
#bdd.setDatabaseName("fichiers.sqlite")
#bdd.open()
#
#query = QtSql.QSqlQuery("fichiers.sqlite")
#query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
             #doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
             #liked INTEGER, url TEXT)")


def listDoi():

    """Function to get the doi from the database"""

    list_doi = []

    query = QtSql.QSqlQuery("fichiers.sqlite")
    query.exec_("SELECT doi FROM papers")

    while query.next():
        record = query.record()
        list_doi.append(record.value('doi'))

    return list_doi


def like(id_bdd, logger):

    """Function to like a post"""

    request = "UPDATE papers SET liked = ? WHERE id = ?"
    params = (1, id_bdd)

    query = QtSql.QSqlQuery("fichiers.sqlite")

    query.prepare(request)

    for value in params:
        query.addBindValue(value)

    query.exec_()


def unLike(id_bdd, logger):

    """Function to unlike a post"""

    request = "UPDATE papers SET liked = ? WHERE id = ?"
    params = (None, id_bdd)

    query = QtSql.QSqlQuery("fichiers.sqlite")

    query.prepare(request)

    for value in params:
        query.addBindValue(value)

    query.exec_()


##def markRead(id_bdd, test=False, logger=None):

    ##"""Fonction pr marquer un torrent comme lu en bdd"""

    ##request = "UPDATE pirate SET new = ? WHERE id = ?"
    ##params = (False, id_bdd)

    ##if not test:
        ###On utilise le Sql de PyQt, évite les conflits
        ##query = QtSql.QSqlQuery("fichiers.sqlite")

        ##query.prepare(request)

        ###On fixe chaque variable à chaque placeholder
        ##for value in params:
            ##query.addBindValue(value)

        ##query.exec_()

    ##else:
        ##bdd = sqlite3.connect("fichiers.sqlite")
        ##bdd.row_factory = sqlite3.Row 
        ##c = bdd.cursor()

        ##c.execute(request, params)

        ##bdd.commit()
        ##c.close()
        ##bdd.close()


def loadPosts(site, logger):

    """Gathers the data and put them in database"""

    feed = feedparser.parse(site)
    journal = feed['feed']['title']

    print(len(feed.entries))

    i = 0

    for entry in feed.entries:

        doi = hosts.getDoi(journal, entry)
        list_doi = listDoi()

        if doi in list_doi:
            logger.debug("Post already in db")
            continue

        title, journal_abb, date, authors, abstract, graphical_abstract, url = hosts.getData(journal, entry)

        query = QtSql.QSqlQuery("fichiers.sqlite")

        query.prepare("INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract, url) VALUES(?, ?, ?, ?, ?, ?, ?, ?)")

        params = (doi, title, date, journal_abb, authors, abstract, graphical_abstract, url)

        for value in params:
            query.addBindValue(value)

        retour = query.exec_()
        #print(retour)

        #logger.debug(query.lastQuery())
        #logger.debug(query.lastError().text())

        if not retour:
            for p in params:
                print(type(p))
                print(p)
            logger.debug(query.lastError().text())
            logger.debug(query.lastQuery())
        else:
            i += 1
            print(i)
            logger.debug("{1} Adding {0} to the database".format(title, journal))


    logger.info("{0}: {1} entries added".format(journal, i))


def parse(logger, parent=None):

    """Function wich starts a worker on every website"""

    #Monitoring time
    start_time = datetime.datetime.now()

    #List of the flux to parse
    #flux = ["ang.xml", "jacs.xml"]
    #flux = ["ang.xml"]
    #flux = ["jacs.xml"]
    flux = ["http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773",
            "http://feeds.feedburner.com/acs/jacsat"
           ]
    #flux = ["http://feeds.feedburner.com/acs/jacsat"]
    #flux = ["http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773"]


    with ThreadPoolExecutor(max_workers=10) as e:
     
        futures_and_posts = {e.submit(loadPosts, site, logger): site for site in flux}

        #for future in as_completed(futures_and_posts):

            #print("worker completed")

            #Display the exception if an error occured
            #if future.exception() is not None:
                #logger.debug((future.exception()))

    #parent.modele.select()
    parent.parseAction.setEnabled(True)

    elsapsed_time = datetime.datetime.now() - start_time
    logger.info(elsapsed_time.total_seconds())
    logger.info("Parsing new articles finished")




if __name__ == "__main__":
    #like(1)
    #like(10)
    #like(15)
    parse(l)
    pass
