#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import datetime
import feedparser
from PyQt4 import QtSql
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

#Personal modules
from log import MyLog
import hosts


#bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE");
#bdd.setDatabaseName("fichiers.sqlite");
#bdd.open()


def listDoi():

    """Fonction qui récupère les id de ts les posts"""

    list_doi = []
    #liste_response = []

    #On utilise le Sql de PyQt, évite les conflits
    query = QtSql.QSqlQuery("fichiers.sqlite")
    query.exec_("SELECT doi FROM papers")

    while query.next():
        record = query.record()
        list_doi.append(record.value('doi'))
        #liste_response.append(record.value('response'))

    return list_doi




def like(id_bdd):

    request = "UPDATE papers SET liked = ? WHERE id = ?"
    params = (1, id_bdd)

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

    print(site)

    list_doi = listDoi()

    for entry in feed.entries:

        print(entry.title)

        doi, title, date, authors, abstract, graphical_abstract = hosts.getData(journal, entry)
        #results = hosts.getData(journal, entry)

        #for element in results:
            #print(element)
        request = "INSERT INTO papers(doi, title, date, journal, authors, abstract, graphical_abstract) \
                   VALUES (?, ?, ?, ?, ?, ?, ?)"
        query = QtSql.QSqlQuery("fichiers.sqlite")

        if doi not in list_doi:

            query.prepare(request)

            params = (doi, title, date, journal, authors, abstract, graphical_abstract)

            #On fixe chaque variable à chaque placeholder
            for value in params:
                query.addBindValue(value)

            query.exec_()


def parse(logger, modele):

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


    with ThreadPoolExecutor(max_workers=10) as e:
     
        futures_and_posts = {e.submit(loadPosts, site, logger): site for site in flux}

        for future in as_completed(futures_and_posts):

            #Display the exception if an error occured
            if future.exception() is not None:
                logger.debug((future.exception()))

            modele.select()


    elsapsed_time = datetime.datetime.now() - start_time
    logger.info(elsapsed_time.total_seconds())
    logger.info("Parsing new articles finished")




if __name__ == "__main__":
    like(1)
    like(10)
    like(15)
    pass
