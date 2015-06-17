#!/usr/bin/python
# -*-coding:Utf-8 -*

from PyQt4 import QtSql, QtCore

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction import text

# DEBUG
import datetime

from log import MyLog

from memory_profiler import profile

class Predictor(QtCore.QThread):

    """Object to predict the percentage match of an article,
    based on its abstract"""

    def __init__(self, logger, bdd=None):

        QtCore.QThread.__init__(self)

        self.x_train = []
        self.y_train = []
        self.classifier = None

        self.bdd = bdd

        self.l = logger

        self.getStopWords()
        self.initializePipeline()


    def __del__(self):

        """Method to destroy the thread properly"""

        self.l.debug("Deleting thread")
        self.exit()


    def getStopWords(self):

        """Method to get english stop words
        + a list of personnal stop words"""

        my_additional_stop_words = []

        with open('config/stop_words.txt', 'r') as config:
            for word in config.readlines():
                my_additional_stop_words.append(word.replace("\n", ""))

        self.stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)


    def initializePipeline(self):

        """Initialize the pipeline for text analysis"""

        start_time = datetime.datetime.now()

        if self.bdd is None:
            self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
            self.bdd.setDatabaseName("fichiers.sqlite")
            self.bdd.open()

        query = QtSql.QSqlQuery(self.bdd)

        query.exec_("SELECT * FROM papers WHERE new=0")

        while query.next():
            record = query.record()

            if type(record.value('abstract')) is str:
                abstract = record.value('abstract')
            else:
                continue

            if type(record.value('title')) is str:
                title = record.value('title')
            else:
                continue

            if type(record.value('liked')) is int:
                category = 0
            else:
                category = 1

            self.x_train.append(abstract + ' ' + title)
            self.y_train.append(category)

        if not self.x_train or 1 not in self.y_train:
            self.l.debug("Not enough data yet")
            return None

        self.x_train = np.array(self.x_train)
        self.y_train = np.array(self.y_train)

        self.classifier = Pipeline([
            ('vectorizer', CountVectorizer(
                            stop_words=self.stop_words)),
            ('tfidf', TfidfTransformer()),
            ('clf', MultinomialNB())])

        try:
            self.classifier.fit(self.x_train, self.y_train)
        except ValueError:
            self.l.debug("Not enough data yet")
            return

        elsapsed_time = datetime.datetime.now() - start_time
        self.l.debug("Initializing classifier in {0}".format(elsapsed_time))


    # @profile
    # def calculatePercentageMatch(self, test=False):
    def run(self):

        """Calculate the match percentage for each article,
        based on the abstract text and the liked articles"""

        self.l.debug("Starting calculations of match percentages")
        start_time = datetime.datetime.now()

        query = QtSql.QSqlQuery(self.bdd)

        query.exec_("SELECT id, abstract FROM papers")

        list_id = []
        x_test = []

        while query.next():

            record = query.record()

            if type(record.value('abstract')) is str:
                abstract = record.value('abstract')

                list_id.append(record.value('id'))
                x_test.append(abstract)

        try:
            # Normalize the percentages: the highest is set to 100%
            list_percentages = [float(100 * proba[0]) for proba in self.classifier.predict_proba(x_test)]
            list_percentages = [perc * 100 / max(list_percentages) for perc in list_percentages]
        except ValueError:
            self.l.debug("Not enough data yet")
            return

        self.bdd.transaction()
        query = QtSql.QSqlQuery(self.bdd)

        query.prepare("UPDATE papers SET percentage_match = ? WHERE id = ?")

        for id_bdd, percentage in zip(list_id, list_percentages):

            params = (percentage, id_bdd)

            for value in params:
                query.addBindValue(value)

            query.exec_()

        if self.bdd.commit():
            self.l.debug("updates ok")

        elsapsed_time = datetime.datetime.now() - start_time
        self.l.debug("Done calculating match percentages in {0} s".format(elsapsed_time))



if __name__ == "__main__":
    logger = MyLog()
    predictor = Predictor(logger)
    predictor.calculatePercentageMatch(True)
