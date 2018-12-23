#!/usr/bin/python
# coding: utf-8

import os
import sys
from typing import Dict
from PyQt5 import QtSql
import re

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from log import MyLog
import functions as fct


class BaseCompany():

    journal_abb: str

    def __init__(self, url: str) -> None:

        self.l = MyLog("activity.log")
        self.url = url

        pass

    def data_completeness(self, bdd: QtSql.QSqlDatabase) -> Dict[str, bool]:

        """
        Function to get the DOIs stored in db for this journal.
        Also returns a list of booleans to check if the data is complete

        Arguments:
            bdd (QtSql.QSqlDatabase): database, initialized in main window

        Returns:
            Dict[str, bool]: dict with DOI as key, and a bool to check if the
                             graphical_abstract was downloaded for the DOI
        """

        query = QtSql.QSqlQuery(bdd)
        query.prepare("SELECT * FROM papers WHERE journal=?")
        query.addBindValue(self.journal_abb)
        query.exec_()

        result: Dict[str, bool] = dict()

        while query.next():
            record = query.record()
            doi = record.value('doi')

            not_empty = record.value('graphical_abstract') != "Empty"
            result[doi] = not_empty

        return result

    def reject(self, entry_title: str) -> bool:

        """
        Function called by a Worker object to filter crappy entries.
        Rejects articles like corrigendum, erratum, etc

        Arguments:
            entry_title (str): title of the entry to be checked

        Returns:
            bool: True if entry is rejected, False if it's accepted
        """

        resource_dir, DATA_PATH = fct.getRightDirs()

        # resource_dir = os.path.dirname(os.path.dirname(sys.executable))
        # Load the regex stored in a config file, as filters
        with open(os.path.join(resource_dir, 'config/regex.txt'),
                  'r', encoding='utf-8') as filters_file:
            filters = filters_file.read().splitlines()

        # If one regex matches, reject the entry
        for regex in filters:
            if re.search(regex, entry_title):
                return True

        return False


if __name__ == '__main__':
    company_obj = BaseCompany("http://feeds.feedburner.com/acs/jcisd8")
    pass
