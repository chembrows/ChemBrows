#!/usr/bin/python
# coding: utf-8


from PyQt4 import QtSql, QtCore

import sys
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction import text
from sklearn.svm import LinearSVC
import traceback
import datetime

# DEBUG
# from memory_profiler import profile

# Personal
from log import MyLog


class Predictor(QtCore.QThread):

    """Object to predict the percentage match of an article,
    based on its abstract"""

    def __init__(self, logger, to_read_list, bdd=None):

        QtCore.QThread.__init__(self)

        self.to_read_list = to_read_list

        self.x_train = []
        self.y_train = []
        self.classifier = None

        if bdd is None:
            self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE")
            self.bdd.setDatabaseName("fichiers.sqlite")
            self.bdd.open()
        else:
            self.bdd = bdd

        self.l = logger

        self.getStopWords()

        self.calculated_something = False


    def __del__(self):

        """Method to destroy the thread properly"""

        self.wait()
        self.l.debug("Deleting thread")


    def getStopWords(self):

        """Method to get english stop words
        + a list of personnal stop words"""

        my_additional_stop_words = []

        if getattr(sys, "frozen", False):
            resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            resource_dir = '.'

        with open(os.path.join(resource_dir, 'config/stop_words.txt'), 'r') as config:
            for word in config.readlines():
                my_additional_stop_words.append(word.rstrip())

        self.stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)


    def initializePipeline(self):

        """Initialize the pipeline for text analysis. 0 is the liked class"""

        start_time = datetime.datetime.now()

        query = QtSql.QSqlQuery(self.bdd)

        query.exec_("SELECT * FROM papers WHERE new=0")

        while query.next():
            record = query.record()
            abstract = record.value('topic_simple')
            id_bdd = record.value('id')

            # Do not use 'Empty' abstracts
            if type(abstract) is not str or abstract == 'Empty':
                continue

            liked = record.value('liked')
            if type(liked) is int and liked == 1:
                category = 0
            else:
                # Do not count the read and not liked articles if the articles
                # are in the waiting list
                if id_bdd not in self.to_read_list:
                    category = 1
                else:
                    continue

            self.x_train.append(abstract)
            self.y_train.append(category)

        # To count for RuntimeWarning: divide by zero encountered in log
        if (not self.x_train or 0 not in self.y_train or
                1 not in self.y_train):
            self.l.error("Not enough data yet to feed the classifier")
            return

        self.classifier = Pipeline([
            ('vectorizer', CountVectorizer(stop_words=self.stop_words)),
            ('tfidf', TfidfTransformer()),
            ('clf', LinearSVC())])

        try:
            self.classifier.fit(self.x_train, self.y_train)
        except ValueError:
            self.l.error("Not enough data yet to train the classifier")
            return

        elapsed_time = datetime.datetime.now() - start_time
        self.l.debug("Initializing classifier in {0}".format(elapsed_time))

        return True


    # @profile
    # def calculatePercentageMatch(self):
    def run(self):

        """Calculate the match percentage for each article,
        based on the abstract text and the liked articles"""

        self.l.debug("Starting calculations of match percentages")
        start_time = datetime.datetime.now()

        query = QtSql.QSqlQuery(self.bdd)

        query.exec_("SELECT id, topic_simple FROM papers")

        list_id = []
        x_test = []

        while query.next():
            record = query.record()
            abstract = record.value('topic_simple')
            x_test.append(abstract)
            list_id.append(record.value('id'))

        try:
            # Normalize the percentages: the highest is set to 100%
            # http://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
            x_test = self.classifier.decision_function(x_test)

            elapsed_time = datetime.datetime.now() - start_time
            self.l.debug("Classifier predicted proba in {}".format(elapsed_time))
            diff_time = datetime.datetime.now()

            maximum = max(x_test)
            minimum = min(x_test)
            list_percentages = 100 - (x_test - minimum) * 100 / (maximum - minimum)

            self.l.debug("Classifier normalized proba in {}".
                         format(datetime.datetime.now() - diff_time))

        except AttributeError:
            self.l.error("Not enough data yet to predict probability")
            return
        except Exception as e:
            self.l.error("predictor: {}".format(e))
            self.l.error(traceback.format_exc())
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

        # # Set the percentage_match to 0 if the abstact is 'Empty' or empty
        # query.prepare("UPDATE papers SET percentage_match = 0 WHERE abstract = 'Empty' OR abstract = ''")
        # query.exec_()

        if not self.bdd.commit():
            self.l.critical("Percentages match not correctly written in db")
        else:
            elapsed_time = datetime.datetime.now() - start_time
            self.l.info("Done calculating match percentages in {0} s".format(elapsed_time))

        self.calculated_something = True


if __name__ == "__main__":
    logger = MyLog("test.log")
    predictor = Predictor(logger)
    predictor.initializePipeline()
    predictor.calculatePercentageMatch()
