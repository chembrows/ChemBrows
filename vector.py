#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import numpy as np

#Pour les modules persos
sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt

import feedparser


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


#feed = feedparser.parse("http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773")
feed = feedparser.parse("test.xml")

#print(feed['feed']['title'])

content = []

for entry in feed.entries:
    #print(entry.title)
    #print(entry.author)
    #print(entry.content[0].value)
    #print(entry.summary)
    #print(batbelt.strip_tags(entry.summary))
    #print("\n")
    content.append(batbelt.strip_tags(entry.summary))
    #break


#vectorizer = CountVectorizer(min_df=1)
vectorizer = CountVectorizer()

counts = vectorizer.fit_transform(content)

tfidf_transformer = TfidfTransformer()
counts_tfidf = tfidf_transformer.fit_transform(counts)
print(counts_tfidf.shape)




#if __name__ == "__main__":
    #pass

