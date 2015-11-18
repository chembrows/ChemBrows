#!/usr/bin/python
# coding: utf-8


import os
import logging
from logging.handlers import RotatingFileHandler


class MyLog(logging.Logger):

    """ Création d'un logger personnalisé. Un logger simple, déjà
    configuré, est généré à l'appel de la classe. Il écrit dans le
    fichier activity.log, et dans la console.
    on peut logger avec logger.(info|warn|debug|error|critical).
    http://sametmax.com/ecrire-des-logs-en-python/ """

    def __init__(self, output_file, total=True):

        super(MyLog, self).__init__(self)

        # on met le niveau du logger à DEBUG, comme ça il écrit tout
        self.setLevel(logging.DEBUG)

        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        if total:
            self.formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        else:
            self.formatter = logging.Formatter('%(message)s')

        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        self.file_handler = RotatingFileHandler(output_file, 'a', 1000000, 1)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.addHandler(self.file_handler)

        # création d'un second handler qui va rediriger chaque écriture de log
        # sur la console
        self.steam_handler = logging.StreamHandler()
        self.steam_handler.setLevel(logging.DEBUG)
        self.addHandler(self.steam_handler)


if __name__ == '__main__':

    # Après 3 heures, on peut enfin logguer
    # Il est temps de spammer votre code avec des logs partout :
    log = MyLog()
    log.info('Hello')
    log.warning('Testing %s', 'foo')
