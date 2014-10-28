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
    query.exec_("SELECT doi, verif FROM papers")

    while query.next():
        record = query.record()
        list_doi.append(record.value('doi'))

        if record.value('verif') == 1:
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


def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("fichiers.sqlite")
    bdd.row_factory = sqlite3.Row 
    c = bdd.cursor()

    c.execute("SELECT verif FROM papers")

    for ligne_bdd in c.fetchall():

        if ligne_bdd['verif'] == 0:
            print("boum")

        #for info in ligne_bdd:
            #print(type(info))


    bdd.commit()
    c.close()
    bdd.close()




if __name__ == "__main__":
    #like(1)
    #like(10)
    #like(15)
    #checkData()
    _, dois = listDoi()
    print(dois)
    pass
