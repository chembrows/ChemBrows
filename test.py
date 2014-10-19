#!/usr/bin/python
# -*-coding:Utf-8 -*

#import sys
#import os
#from requests import get
#import numpy as np
#import pygal
#from pygal.style import RedBlueStyle
#import pickle # sauvegarder des objets

##Pour les modules persos
#sys.path.append('/home/djipey/informatique/python/batbelt')
#from easyxls import EasyXls
#import batbelt

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier


#http://stackoverflow.com/questions/21088853/how-to-get-nbest-predictions-from-sklearn-naive-bayes-classifier-python
#http://stackoverflow.com/questions/11807649/simple-example-using-bernoullinb-naive-bayes-classifier-scikit-learn-in-python

X_train = np.array(["new york is a hell of a town",
                    "new york was originally dutch",
                    "the big apple is great",
                    "new york is also called the big apple",
                    "nyc is nice",
                    "people abbreviate new york city as nyc",
                    "the capital of great britain is london",
                    "london is in the uk",
                    "london is in england",
                    "london is in great britain",
                    "it rains a lot in london",
                    "london hosts the british museum",
                    "new york is great and so is london",
                    "i like london better than new york"])

#y_train_text = [["new york"],["new york"],["new york"],["new york"],["new york"],
                #["new york"],["london"],["london"],["london"],["london"],
                #["london"],["london"],["new york","london"],["new york","london"]]

y_train_text = np.array([ 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1])

X_test = np.array(['nice day in nyc',
                   'welcome to london',
                   'london is rainy',
                   'it is raining in britian',
                   'it is raining in britian and the big apple',
                   'it is raining in britian and nyc',
                   'hello welcome to new york. enjoy it here and london too'])

target_names = ['New York', 'London']

#lb = preprocessing.MultiLabelBinarizer()
#Y = lb.fit_transform(y_train_text)

#print(Y)
#print(type(Y))

classifier = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    #('clf', OneVsRestClassifier(LinearSVC()))])
    ('clf', MultinomialNB())])


print(target_names)

print(classifier.fit(X_train, y_train_text).predict_proba(X_test))

predicted = classifier.predict(X_test)
#all_labels = lb.inverse_transform(predicted)

#print(predicted)
#print(np.mean(predicted == X_train))

for item, labels in zip(X_test, predicted):
    labels = target_names[labels]
    print(item, labels)







#if __name__ == "__main__":
    #pass

