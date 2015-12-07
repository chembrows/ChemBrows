#!/usr/bin/python
# coding: utf-8


import os
import logging
from logging.handlers import RotatingFileHandler


class MyLog(logging.Logger):

    """Création d'un logger personnalisé. Un logger simple, déjà
    configuré, est généré à l'appel de la classe. Il écrit dans le
    fichier activity.log, et dans la console.
    Custom logger class. A pre-configured logger is created when the class
    is called. Writes into the terminal and in activity.log.
    Use: logger.(info|warn|debug|error|critical)
    http://sametmax.com/ecrire-des-logs-en-python/"""

    def __init__(self, output_file, total=True):

        super(MyLog, self).__init__(self)

        # Set the logging level to DEBUG
        self.setLevel(logging.DEBUG)

        # Set the format of te output
        if total:
            self.formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        else:
            self.formatter = logging.Formatter('%(message)s')

        # Create a handler, redirects the output to a file in 'append' mode, w/
        # a backup and a mx size of 1 Mo
        self.file_handler = RotatingFileHandler(output_file, 'a', 1000000, 1)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.addHandler(self.file_handler)

        # Second handler to get the output into the terminal
        self.steam_handler = logging.StreamHandler()
        self.steam_handler.setLevel(logging.DEBUG)
        self.addHandler(self.steam_handler)


if __name__ == '__main__':
    log = MyLog()
    log.info('Hello')
    log.warning('Testing %s', 'foo')
