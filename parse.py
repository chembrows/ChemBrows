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


#def markDled(id_bdd, test=False, logger=None):

    #"""Fonction pr marquer un torrent comme lu en bdd"""

    #request = "UPDATE pirate SET dled = ? WHERE id = ?"
    #params = (True, id_bdd)

    #if not test:
        ##On utilise le Sql de PyQt, évite les conflits
        #query = QtSql.QSqlQuery("fichiers.sqlite")

        ##query.prepare(request)

        ###On fixe chaque variable à chaque placeholder
        ##for value in params:
            ##query.addBindValue(value)

        ##query.exec_()

    #else:
        #bdd = sqlite3.connect("fichiers.sqlite")
        ##bdd.row_factory = sqlite3.Row 
        ##c = bdd.cursor()

        ##c.execute(request, params)

        ##bdd.commit()
        ##c.close()
        ##bdd.close()


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

    request = "INSERT INTO papers(percentage_match, title, date, journal, authors, abstract, graphical_abstract) \
               VALUES (?, ?, ?, ?, ?, ?, ?)"
    query = QtSql.QSqlQuery("fichiers.sqlite")

    feed = feedparser.parse(site)
    journal = feed['feed']['title']

    for entry in feed.entries:

        #title, date, authors, abstract, graphical_abstract = hosts.getData(journal, entry)
        results = hosts.getData(journal, entry)

        for element in results:
            print(element)

        #TODO: calculer le percentage_match ici

        #query.prepare(request)

        #params = (percentage_match, title, date, journal, authors, abstract, graphical_abstract)

        #On fixe chaque variable à chaque placeholder
        #for value in params:
            #query.addBindValue(value)

        #query.exec_()


def parse(logger):

    """Function wich starts a worker on every website"""

    #Monitoring time
    start_time = datetime.datetime.now()

    #List of the flux to parse
    flux = ["ang.xml", "jacs.xml"]
    #flux = ["jacs.xml"]

    with ThreadPoolExecutor(max_workers=10) as e:
     
        futures_and_posts = {e.submit(loadPosts, site, logger): site for site in flux}

        for future in as_completed(futures_and_posts):

            #Display the exception if an error occured
            if future.exception() is not None:
                logger.debug((future.exception()))


    elsapsed_time = datetime.datetime.now() - start_time
    logger.info(elsapsed_time.total_seconds())
    logger.info("Parsing new articles finished")




if __name__ == "__main__":
    pass
