#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
#import datetime
#import feedparser
from PyQt4 import QtSql
import sqlite3
import arrow
import unidecode
import re


#TEST
from bs4 import BeautifulSoup

#Personal modules
from log import MyLog
import hosts


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


def simpleChar(string):

    """Sluggify the string"""
    #http://www.siteduzero.com/forum-83-810635-p1-sqlite-recherche-avec-like-insensible-a-la-casse.html#r7767300

    #http://stackoverflow.com/questions/5574042/string-slugification-in-python
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', ' ', string)


def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("fichiers.sqlite")
    bdd.row_factory = sqlite3.Row 
    c = bdd.cursor()

    c.execute("SELECT * FROM papers")

    c.execute("ALTER TABLE papers DROP COLUMN abstract_simple")
    #c.execute("ALTER TABLE papers DROP COLUMN abstract_simple")
    #c.execute("UPDATE papers SET new=0 WHERE new='false'")


    #for ligne_bdd in c.fetchall():
        #title = ligne_bdd['title']
        #abstract = ligne_bdd['abstract']
        #id_bdd = ligne_bdd['id']

        #if abstract is not None:
            #topic_simple = simpleChar(BeautifulSoup(abstract).text) + simpleChar(title)
            #print(topic_simple)
            #c.execute("UPDATE papers SET topic_simple=? WHERE id=?", (topic_simple, id_bdd))

    bdd.commit()
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
