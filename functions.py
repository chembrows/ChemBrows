#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import datetime
import feedparser
from PyQt4 import QtSql
#import concurrent.futures
#from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sqlite3
import arrow

#TEST
import collections

#Personal modules
from log import MyLog
import hosts


#l = MyLog(total=True)
#l.setLevel(logging.DEBUG)

#bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
#bdd.setDatabaseName("fichiers.sqlite")
#bdd.open()

#query = QtSql.QSqlQuery("fichiers.sqlite")
#query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
             #doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
             ##liked INTEGER, url TEXT, check INTEGER)")


def listDoi():

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
            #Try to download the images again if it didn't work before
            list_ok.append(True)
        else:
            list_ok.append(False)

    return list_doi, list_ok


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


def prettyDate(date):

    """Prettify a date. Ex: 3 days ago"""

    now = arrow.now()
    date = arrow.get(date)

    if now.timestamp - date.timestamp < 86400:
        return "Today"
    else:
        return date.humanize(now.naive)



def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("fichiers.sqlite")
    bdd.row_factory = sqlite3.Row 
    c = bdd.cursor()

    c.execute("SELECT * FROM papers")
    #c.execute("UPDATE papers SET new=1 WHERE new='true'")
    #c.execute("UPDATE papers SET new=0 WHERE new='false'")

    dois = []

    for ligne_bdd in c.fetchall():

        dois.append(ligne_bdd['doi'])

    for doi in dois:
        if " " in doi:
            print(doi)
            #old_doi = doi
            #new_doi = doi.replace(" ", "")
            #c.execute("UPDATE papers SET doi=? WHERE doi=?", (new_doi, old_doi))

    #print(len(dois))
    #print(len(list(set(dois))))

    ##print([x for x, y in collections.Counter(dois).items() if y > 1])
    #duplicates = [x for x, y in collections.Counter(dois).items() if y > 1]


    #titles = []
    #for doi in duplicates:

        #c.execute("SELECT * FROM papers WHERE doi=?", (doi,))
        ##c.execute("DELETE FROM papers WHERE doi=?", (doi,))
        ##titles.append(c.fetchone()['title'])

    #print(len(titles))


    #bdd.commit()
    c.close()
    bdd.close()



if __name__ == "__main__":
    #like(1)
    #like(10)
    #like(15)
    checkData()
    #_, dois = listDoi()
    #print(dois)
    pass
