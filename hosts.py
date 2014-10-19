#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import feedparser
from bs4 import BeautifulSoup
import requests
from io import open as iopen

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
        soup = BeautifulSoup(entry.summary)

        r = soup.find_all("a", attrs={"class": "figZoom"})

        if len(r) == 1:
            response, graphical_abstract = downloadPic(r[0]['href'])


    if journal == "Journal of the American Chemical Society: Latest Articles (ACS Publications)":
        title = entry.title.replace("\n", " ")
        abstract = None

        try:
            #Dl of the article website page
            page = requests.get(entry.feedburner_origlink, timeout=3)

            #If the dl went wrong, print an error
            if page.status_code is not requests.codes.ok:
                print("getData, JACS, bad return code: {0}".format(page.status_code))

            #Get the abstract
            soup = BeautifulSoup(page.text)
            r = soup.find_all("p", attrs={"class": "articleBody_abstractText"})

            if len(r) == 1:
                abstract = r[0].text

        except requests.exceptions.Timeout:
            print("getData, JACS, timeout")

        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("img", alt="TOC Graphic")

        if len(r) == 1:
            response, graphical_abstract = downloadPic(r[0]['src'])

    return title, entry.date, entry.author, abstract, graphical_abstract



def downloadPic(url):

    """The parameter is a list. The function will be able to evolve"""

    #On essaie de récupérer chaque page correspondant
    #à chaque url, ac un timeout
    try:
        #On utilise un user-agent de browser,
        #ds le cas où les hébergeurs bloquent les bots
        headers = {'User-agent': 'Mozilla/5.0'}

        #On rajoute l'url de base comme referer,
        #car certains sites bloquent l'accès direct aux images
        headers["Referer"]= url

        page = requests.get(url, timeout=3, headers=headers)

        #Si la page a bien été récupérée
        if page.status_code == requests.codes.ok:

            path = "./graphical_abstracts/"

            #On enregistre la page
            with iopen(path + batbelt.simpleChar(url), 'wb') as file:
                file.write(page.content)
                #l.debug("image ok")

                #On sort True si on matche une des possibilités
                #de l'url
                return True, batbelt.simpleChar(url)

        #Si la page n'est pas téléchargée et qu'on est à la dernière
        #url de la liste
        elif page.status_code != requests.codes.ok and url == list_urls[-1]:
            print("Bad return code: {0}".format(page.status_code))
            return "wrongPage", None

    except requests.exceptions.Timeout:
        print("downloadPic, timeout")
        return "timeOut", None



if __name__ == "__main__":

    #urls_test = ["ang.xml",
                 ##"jacs.xml"
                #]
    urls_test = ["jacs.xml"]

    for site in urls_test:

        feed = feedparser.parse(site)

        #Name of the journal
        journal = feed['feed']['title'] 

        for entry in feed.entries:
            for element in getData(journal, entry):
                print(element)
                break
            break

        print("\n\n")

