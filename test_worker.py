#!/usr/bin/python
# -*-coding:Utf-8 -*

import os
import pytest
from PyQt4 import QtSql, QtCore
import random
import logging

from worker import Worker
from log import MyLog
import hosts


@pytest.fixture()
def journalsUrls():

    urls = []
    _, rsc_abb, rsc_urls = hosts.getJournals("rsc")
    _, acs_abb, acs_urls = hosts.getJournals("acs")
    _, wiley_abb, wiley_urls = hosts.getJournals("wiley")
    _, npg_abb, npg_urls = hosts.getJournals("npg")
    _, science_abb, science_urls = hosts.getJournals("science")


    urls = rsc_urls + acs_urls + wiley_urls + npg_urls + science_urls

    return urls


@pytest.fixture()
def connectionBdd():

    try:
        os.remove("./debug/test.sqlite")
        for filename in os.listdir("./debug/graphical_abstracts/") :
                os.remove("./debug/graphical_abstracts/" + filename)
    except FileNotFoundError:
        pass

    bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    bdd.setDatabaseName("./debug/test.sqlite")

    bdd.open()

    query = QtSql.QSqlQuery("./debug/test.sqlite")
    query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match REAL, \
                 doi TEXT, title TEXT, date TEXT, journal TEXT, authors TEXT, abstract TEXT, graphical_abstract TEXT, \
                 liked INTEGER, url TEXT, verif INTEGER, new INTEGER, topic_simple TEXT)")

    return bdd


@pytest.fixture()
def createLogger():

    logger = MyLog()

    # Set the logging level to Error (debugging)
    logger.setLevel(logging.INFO)

    return logger


def test_worker(journalsUrls, connectionBdd, createLogger, qtbot):

    logger = createLogger
    bdd = connectionBdd
    # list_sites = journalsUrls
    list_sites = ["debug/nat.xml"]

    # for site in random.sample(list_sites, 3):
    for site in list_sites:

        worker = Worker(site, logger, bdd)
        worker.path = "./debug/graphical_abstracts/"
        worker.start()
        break
