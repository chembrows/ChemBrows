#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import re
import datetime
import feedparser

from PyQt4 import QtSql

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

from http.client import BadStatusLine
from socket import timeout

#from misc import simpleChar
#from misc import strByteToOctet 

from log import MyLog
#import hosts # Infos sur comment gérer les hosts

sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt



def markDled(id_bdd, test=False, logger=None):

    """Fonction pr marquer un torrent comme lu en bdd"""

    request = "UPDATE pirate SET dled = ? WHERE id = ?"
    params = (True, id_bdd)

    if not test:
        #On utilise le Sql de PyQt, évite les conflits
        query = QtSql.QSqlQuery("fichiers.sqlite")

        query.prepare(request)

        #On fixe chaque variable à chaque placeholder
        for value in params:
            query.addBindValue(value)

        query.exec_()

    else:
        bdd = sqlite3.connect("fichiers.sqlite")
        bdd.row_factory = sqlite3.Row 
        c = bdd.cursor()

        c.execute(request, params)

        #bdd.commit()
        #c.close()
        #bdd.close()


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

    """Récupère les infos de chaque torrent pr les mettre en bdd.
    Récupère ts les urls dans les infos d'un torrent et les passe
    à la fct downloadPic pr qu'elle télécharge les images.
    Écrit en bdd les torrents traités"""

    feed = feedparser.parse(site)

    #print(feed['feed']['title'])

    request = "INSERT INTO papers(percentage_match, title, date, journal, abstract, graphical_abstract) VALUES (?, ?, ?, ?, ?, ?)"

    query = QtSql.QSqlQuery("fichiers.sqlite")


    for entry in feed.entries:

        title, date, journal, abstract, graphical_abstract = hosts.getData(entry)

        #TODO: calculer le percentage_match ici

        query.prepare(request)

        params = (percentage_match, entry.title, entry.date, journal, abstract, graphical_abstract)

        #On fixe chaque variable à chaque placeholder
        for value in params:
            query.addBindValue(value)

        query.exec_()


def parse(logger):

    """Fct qui sert à lancer les workers (sorte de threads)
    sur chaque torrent d'une page de tpb. Elle ne parse pas
    à proprement parlé, elle délègue cette tâche à d'autres fct"""

    #On démarre un timer pr chronométrer les tâches
    start_time = datetime.datetime.now()

    #liste des flux à parser
    flux = ["test.xml", "http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773"]

    # Un pool executor est un context manager qui va automatiquement créer des
    # processus Python séparés et répartir les tâches qu'on va lui envoyer entre
    # ces processus (appelés workers, ici on en utilise 5).
    with ThreadPoolExecutor(max_workers=10) as e:
     
        # On e.submit() envoie les tâches à l'executor qui les dispatch aux
        # workers. Ces derniers appelleront "load_url(url)". "e.submit()" retourne
        # une structure de données appelées "future", qui représente  un accès au
        # résultat asynchrone, qu'il soit résolu ou non.
        try:
            futures_and_posts = {e.submit(loadPosts, site, logger): site for site in flux}
        except BadStatusLine:
            l.debug("Erreur API")

        # "as_completed()" prend un iterable de future, et retourne un générateur
        # qui itère sur les futures au fur et à mesures que celles
        # ci sont résolues. Les premiers résultats sont donc les premiers arrivés,
        # donc on récupère le contenu des sites qui ont été les premiers à répondre
        # en premier, et non dans l'ordre des URLS.
        for future in as_completed(futures_and_posts):

            # On affiche le résultats contenu des sites si les futures le contienne.
            # Si elles contiennent une exception, on affiche l'exception.
            if future.exception() is not None:
                logger.debug((future.exception()))

    if logger is not None:
        logger.info("Traitement des torrents terminés")
    else:
        l.info("Traitement des torrents terminés")


if __name__ == "__main__":
    pass
