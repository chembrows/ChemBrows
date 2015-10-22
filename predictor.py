#!/usr/bin/python
# coding: utf-8


from PyQt4 import QtSql, QtCore

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction import text

# DEBUG
import datetime
from memory_profiler import profile

from log import MyLog


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

        self.calculated_something = False


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
                my_additional_stop_words.append(word.rstrip())

        self.stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)


    def initializePipeline(self):

        """Initialize the pipeline for text analysis. 0 is the liked class"""

        start_time = datetime.datetime.now()

        if self.bdd is None:
            self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
            self.bdd.setDatabaseName("fichiers.sqlite")
            self.bdd.open()

        query = QtSql.QSqlQuery(self.bdd)

        query.exec_("SELECT * FROM papers WHERE new=0")

        while query.next():
            record = query.record()

            abstract = record.value('abstract')

            # Do not use 'Empty' abstracts
            if type(abstract) is not str or abstract == 'Empty':
                continue

            liked = record.value('liked')
            if type(liked) is int and liked == 1:
                category = 0
            else:
                category = 1

            self.x_train.append(abstract)
            self.y_train.append(category)

        # To count for RuntimeWarning: divide by zero encountered in log
        if not self.x_train or 0 not in self.y_train or not 1 in self.y_train:
            self.l.error("Not enough data yet to feed the classifier")
            return

        self.classifier = Pipeline([
            ('vectorizer', CountVectorizer(
                            stop_words=self.stop_words)),
            ('tfidf', TfidfTransformer()),
            ('clf', MultinomialNB())])

        try:
            self.classifier.fit(self.x_train, self.y_train)
        except ValueError:
            self.l.error("Not enough data yet to train the classifier")
            return

        elsapsed_time = datetime.datetime.now() - start_time
        self.l.debug("Initializing classifier in {0}".format(elsapsed_time))

        return True


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
            abstract = record.value('abstract')
            x_test.append(abstract)
            list_id.append(record.value('id'))

        try:
            # Normalize the percentages: the highest is set to 100%
            # Use operations on numpy array, faster than lists comprehensions
            x_test = np.array([proba[0] for proba in self.classifier.predict_proba(x_test)])
            maximum = max(x_test)
            list_percentages = x_test * 100 / maximum
        except AttributeError:
            self.l.error("Not enough data yet to predict probability")
            return

        self.bdd.transaction()
        query = QtSql.QSqlQuery(self.bdd)

        query.prepare("UPDATE papers SET percentage_match = ? WHERE id = ?")

        for id_bdd, percentage in zip(list_id, list_percentages):

            # Convert the percentage to a float, because the number is
            # probably a type used by numpy. MANDATORY
            params = (float(percentage), id_bdd)

            for value in params:
                query.addBindValue(value)

            query.exec_()

        # Set the percentage_match to 0 if the abstact is 'Empty' or empty
        query.prepare("UPDATE papers SET percentage_match = 0 WHERE abstract = 'Empty' OR abstract = ''")
        query.exec_()

        if not self.bdd.commit():
            self.l.critical("Percentages match not correctly written in db")
        else:
            elsapsed_time = datetime.datetime.now() - start_time
            self.l.info("Done calculating match percentages in {0} s".format(elsapsed_time))

        self.calculated_something = True


if __name__ == "__main__":
    logger = MyLog()
    predictor = Predictor(logger)
    predictor.initializePipeline()
    predictor.calculatePercentageMatch(True)
