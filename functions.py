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
# from bs4 import BeautifulSoup

#Personal modules
# from log import MyLog
# import hosts


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
    # http://www.siteduzero.com/forum-83-810635-p1-sqlite-recherche-avec-like-insensible-a-la-casse.html#r7767300

    # http://stackoverflow.com/questions/5574042/string-slugification-in-python
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', ' ', string)


def queryString(word):

    """
    Function to return a string formatted to be
    included in a LIKE query
    Ex:
    querySting("sper*m") -> % sper%mine %
    querySting("*sperm*") -> %sperm%
    querySting("spermine") -> % spermine %
    """

    word = str(word)

    if word[0] != '*' and word[-1] != '*' and '*' in word:
        word = word.replace('*', '%')

    res = word.replace('*', '')

    if word[0] == '*':
        res = '%' + res
    else:
        res = '% ' + res

    if word[-1] == '*':
        res = res + '%'
    else:
        res = res + ' %'

    return res


def buildSearch(topic_entries, author_entries):

    """Build the query"""

    base = "SELECT * FROM papers WHERE "

    first = True

    # TOPIC, AND condition
    if topic_entries[0]:
        first = False

        words = [word.lstrip().rstrip() for word in topic_entries[0].split(",")]
        words = [queryString(word) for word in words]

        for word in words:
            if word is words[0]:
                base += "topic_simple LIKE '{0}'".format(word)
            else:
                base += " AND topic_simple LIKE '{0}'".format(word)

    # TOPIC, OR condition
    if topic_entries[1]:
        words = [word.lstrip().rstrip() for word in topic_entries[1].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            base += "topic_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                base += " OR topic_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                base += " OR topic_simple LIKE '{0}'".format(word)

    # TOPIC, NOT condition
    if topic_entries[2]:
        words = [word.lstrip().rstrip() for word in topic_entries[2].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            base += "topic_simple NOT LIKE '{0}'".format(words[0])

            for word in words[1:]:
                base += " AND topic_simple NOT LIKE '{0}'".format(word)
        else:
            for word in words:
                base += " AND topic_simple NOT LIKE '{0}'".format(word)

# Alexander G. Tolstikov, Rimma G. Savchenko, Elena S. Lukina,
# Denis V. Nedopekin, Regina M. Limantceva, Leonard M. Khalilov,
# Ekaterina S. Mescheryakova, Victor N. Odinokov

    # AUTHOR, AND condition
    if author_entries[0]:
        words = [word.lstrip().rstrip() for word in author_entries[0].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(words[0])
            base += "' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(words[0])
            # base += "authors_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " AND authors_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " AND authors_simple LIKE '{0}'".format(word)

    # AUTHOR, OR condition
    if author_entries[1]:
        words = [word.lstrip().rstrip() for word in author_entries[1].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(words[0])
            base += "' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(words[0])
            # base += "authors_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " OR ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " OR ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " OR authors_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " OR ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " OR ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " OR authors_simple LIKE '{0}'".format(word)

    # AUTHOR, NOT condition
    if author_entries[2]:
        words = [word.lstrip().rstrip() for word in author_entries[2].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(words[0])
            base += "', ' || replace(authors, ',', ' ') || ' ,' NOT LIKE '{0}'".format(words[0])
            # base += "authors_simple NOT LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{0}'".format(word)
                # base += " AND authors_simple NOT LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{0}'".format(word)
                # base += " AND authors_simple NOT LIKE '{0}'".format(word)

    return base


def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("debug/test.sqlite")
    bdd.row_factory = sqlite3.Row
    c = bdd.cursor()

    piece1 = "SELECT * FROM papers WHERE authors_simple LIKE '% cottet %' OR authors_simple LIKE '% chamieh %' OR authors_simple LIKE '% boiteau %' OR authors_simple LIKE '% rossi %' OR authors_simple LIKE '% beaufils %'"

    piece2 = " AND journal='ACS Chem. Biol.'"
    print(piece1 + piece2)

    # c.execute(piece1)
    c.execute(piece1 + piece2)

    results = c.fetchall()

    i = 0
    for line in results:
        print(line['title'])
        print(line['journal'])
        i += 1
    print(i)
    c.close()
    bdd.close()



if __name__ == "__main__":
    # like(10)
    # checkData()
    # _, dois = listDoi()
    # print(dois)
    queryString("sper**mine")
    queryString("*sperm*")
    queryString("spermine")
    # checkData()

    pass
