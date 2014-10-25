#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
from PyQt4 import QtSql

#Pour les modules persos
sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt


import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier


#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfTransformer
#from sklearn.naive_bayes import MultinomialNB


##feed = feedparser.parse("http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773")
#feed = feedparser.parse("ang.xml")

#print(feed['feed']['title'])

#content = []

#for entry in feed.entries:
    ##print(entry.title)
    ##print(entry.author)
    ##print(entry.content[0].value)
    ##print(entry.summary)
    ##print(batbelt.strip_tags(entry.summary))
    ##print("\n")
    #content.append(batbelt.strip_tags(entry.summary))
    ##break


##vectorizer = CountVectorizer(min_df=1)
#vectorizer = CountVectorizer()

#counts = vectorizer.fit_transform(content)

#tfidf_transformer = TfidfTransformer()
#counts_tfidf = tfidf_transformer.fit_transform(counts)
#print(counts_tfidf.shape)

#clf = MultinomialNB().fit(counts_tfidf)



class Predictor():


    """Object to predict the percentage match of an article,
    based on its abstract"""


    def __init__(self, bdd=None):


        self.x_train = []
        self.y_train = []
        self.classifier = None

        self.bdd = bdd

        self.initializePipeline()


    def initializePipeline(self):

        if self.bdd is None:
            self.bdd = QtSql.QSqlDatabase.addDatabase("QSQLITE");
            self.bdd.setDatabaseName("fichiers.sqlite");
            self.bdd.open()

        query = QtSql.QSqlQuery("fichiers.sqlite")

        query.exec_("SELECT * FROM papers")

        while query.next():
            record = query.record()

            if type(record.value('abstract')) is str:
                simple_abstract = batbelt.strip_tags(record.value('abstract'))

            if type(record.value('liked')) is not int:
                category = 0
            else:
                category = 1

            self.x_train.append(simple_abstract)
            self.y_train.append(category)

        self.x_train = np.array(self.x_train)
        self.y_train = np.array(self.y_train)

        self.classifier = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', MultinomialNB())])

        self.classifier.fit(self.x_train, self.y_train)


    def calculatePercentageMatch(self, test=False):

        query = QtSql.QSqlQuery("fichiers.sqlite")

        query.exec_("SELECT id, abstract FROM papers")

        list_id = []
        x_test = []

        while query.next():

            record = query.record()

            if type(record.value('abstract')) is str:
                simple_abstract = batbelt.strip_tags(record.value('abstract'))

            list_id.append(record.value('id'))
            x_test.append(simple_abstract)

        x_test = np.array(self.x_train)

        list_percentages = [ round(float(100 * proba[1]), 2) for proba in self.classifier.predict_proba(x_test) ]

        if test:
            print(list_percentages)
        else:
            for id_bdd, percentage in zip(list_id, list_percentages):
                request = "UPDATE papers SET percentage_match = ? WHERE id = ?"
                params = (percentage, id_bdd)

                query = QtSql.QSqlQuery("fichiers.sqlite")

                query.prepare(request)

                for value in params:
                    query.addBindValue(value)

                query.exec_()






if __name__ == "__main__":
    predictor = Predictor()
    predictor.calculatePercentageMatch(True)
    pass

