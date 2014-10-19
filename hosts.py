#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import feedparser
from bs4 import BeautifulSoup
import requests

#Personal modules
sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt


#urls = ["http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773",
        #"http://feeds.feedburner.com/acs/jacsat"
       #]

def getData(journal, entry):

    """Get the data. Starts from the data contained in the RSS flux, and if necessary,
    parse the website for supplementary infos. Download the graphical abstract"""

    #This function is called ike this in parse.py:
    #title, date, authors, abstract, graphical_abstract = hosts.getData(journal, entry)

    if journal == "Angewandte Chemie International Edition":

        abstract = batbelt.strip_tags(entry.summary) 
        title = entry.title

    if journal == "Journal of the American Chemical Society: Latest Articles (ACS Publications)":
        title = entry.title.replace("\n", " ")

        try:
            #Dl of the article website page
            page = requests.get(entry.feedburner_origlink, timeout=3)

            #If the dl went wrong, print an error
            if page.status_code is not requests.codes.ok:
                print("JACS, mauvais code de retour: {0}".format(page.status_code))
                #return False

            #Get the abstract
            soup = BeautifulSoup(page.text)
            r = soup.find_all("p", attrs={"class": "articleBody_abstractText"})

            if len(r) == 1:
                abstract = r[0].text

        except requests.exceptions.Timeout:
            print("JACS, Trop long")


    graphical_abstract = None

    return title, entry.date, entry.author, abstract, graphical_abstract



if __name__ == "__main__":

    urls_test = ["ang.xml",
                 "jacs.xml"
                ]

    for site in urls_test:

        feed = feedparser.parse(site)

        #Name of the journal
        journal = feed['feed']['title'] 

        for entry in feed.entries:
            for element in getData(journal, entry):
                print(element)

