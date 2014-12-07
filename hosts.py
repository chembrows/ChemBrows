#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import os
import feedparser
from bs4 import BeautifulSoup
import requests
from io import open as iopen
import arrow

#Personal modules
sys.path.append('/home/djipey/informatique/python/batbelt')
import batbelt


#urls = ["http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291521-3773",
        #"http://feeds.feedburner.com/acs/jacsat"
       #]

def getData(journal, entry):

    """Get the data. Starts from the data contained in the RSS flux, and if necessary,
    parse the website for supplementary infos. Download the graphical abstract"""

    #This function is called like this in parse.py:
    #title, date, authors, abstract, graphical_abstract = hosts.getData(journal, entry)

    #List of the journals
    rsc, rsc_abb = getJournals("rsc")
    acs, acs_abb = getJournals("acs")
    wiley, wiley_abb = getJournals("wiley")
    npg, npg_abb = getJournals("npg")
    science, science_abb = getJournals("science")

    doi = getDoi(journal, entry)

    #If the journal is edited by the RSC
    if journal in rsc:

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        journal_abb = rsc_abb[rsc.index(journal)]
        url = entry.feedburner_origlink

        abstract = None
        graphical_abstract = None

        soup = BeautifulSoup(entry.summary)

        r = soup.find_all("div")

        author = None

        graphical_abstract = r[0].img
        if graphical_abstract is not None:
            graphical_abstract = r[0].img['src']
            response, graphical_abstract = downloadPic(graphical_abstract)
        else:
            graphical_abstract = "Empty"

        try:
            #Dl of the article website page
            #page = requests.get(entry.feedburner_origlink, timeout=20)
            page = requests.get(url, timeout=20)

            #If the dl went wrong, print an error
            if page.status_code is not requests.codes.ok:
                print("{0}, bad return code: {1}".format(journal_abb, page.status_code))

            #Get the abstract
            soup = BeautifulSoup(page.text)
            r = soup.find_all("meta", attrs={"name": "citation_abstract"})
            if r:
                abstract = r[0]['content']

            r = soup.find_all("meta", attrs={"name": "citation_author"})
            if r:
                author = [ tag['content'] for tag in r ]
                author = ", ".join(author)

        except requests.exceptions.Timeout:
            print("getData, {0}, timeout".format(journal_abb))
        except Exception as e:
            print(e)


    if journal in wiley:

        journal_abb = wiley_abb[wiley.index(journal)]
        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

        author = entry.author.split(", ")
        author = ", ".join(author)

        url = entry.prism_url

        graphical_abstract = None

        abstract = None

        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("a", attrs={"class": "figZoom"})

        if r:
            response, graphical_abstract = downloadPic(r[0]['href'])
            r[0].replaceWith("")
            abstract = soup.renderContents().decode()


    if journal in acs:

        title = entry.title.replace("\n", " ")
        journal_abb = acs_abb[acs.index(journal)]
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        abstract = None

        #If there is only one author
        try:
            author = entry.author.split(" and ")
            author = author[0] + ", " + author[1]
            author = author.split(", ")
            author = ", ".join(author)
        except IndexError:
            author = entry.author

        url = entry.feedburner_origlink

        graphical_abstract = None

        try:
            #Dl of the article website page
            page = requests.get(url, timeout=20)

            #If the dl went wrong, print an error
            if page.status_code is not requests.codes.ok:
                print("getData, {0}, bad return code: {1}".format(journal_abb, page.status_code))

            #Get the abstract
            soup = BeautifulSoup(page.text)
            r = soup.find_all("p", attrs={"class": "articleBody_abstractText"})
            if r:
                abstract = r[0].text
            else:
                abstract = "Empty"

        except requests.exceptions.Timeout:
            print("getData, {0}, timeout".format(journal_abb))
        except Exception as e:
            print(e)

        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("img", alt="TOC Graphic")
        if r:
            response, graphical_abstract = downloadPic(r[0]['src'])
        else:
            graphical_abstract = "Empty"


    if journal in npg:

        title = entry.title
        journal_abb = npg_abb[npg.index(journal)]
        date = entry.date
        url = entry.id
        abstract = entry.summary
        graphical_abstract = None
        author = None

        soup = BeautifulSoup(entry.content[0].value)
        r = soup.find_all("p")

        if r:
            for p in r:
                if "Authors:" in p.text:
                    author = p.text.split("Authors: ")[1].split(", ")

                    if "&" in author[-1]:
                        author = author[:-1] + author[-1].split(" & ")

                    author = ", ".join(author)

        try:
            #Dl of the article website page
            page = requests.get(url, timeout=20)

            #If the dl went wrong, print an error
            if page.status_code is not requests.codes.ok:
                print("getData, {0}, bad return code: {1}".format(journal_abb, page.status_code))

            #Get the abstract
            soup = BeautifulSoup(page.text)
            r = soup.find_all("img", attrs={"class": "fig"})

            if r:
                if "f1.jpg" in r[0]["src"]:
                    graphical_abstract ="http://www.nature.com" + r[0]["src"]

                    if "carousel" in graphical_abstract:
                        graphical_abstract = graphical_abstract.replace("carousel", "images_article")

            if graphical_abstract is not None:
                response, graphical_abstract = downloadPic(graphical_abstract)
            else:
                graphical_abstract = "Empty"

        except requests.exceptions.Timeout:
            print("getData, {0}, timeout".format(journal_abb))
        except Exception as e:
            print(e)


    if journal in science:

        title = entry.title
        journal_abb = science_abb[science.index(journal)]
        date = entry.date
        url = entry.id

        graphical_abstract = "Empty"
        author = None

        abstract = entry.summary

        if "Untangling" in title:
            print("babam")
            print(entry)

        if "Author:" in entry.summary:
            abstract = entry.summary.split("Author: ")[0]
            #author = [entry.summary.split("Author: ")[1]] #To uncomment to get a list of author
            author = entry.summary.split("Author: ")[1]
        elif "Authors:" in entry.summary:
            abstract = entry.summary.split("Authors: ")[0]
            author = entry.summary.split("Authors: ")[1].split(", ")
            author = ", ".join(author) # To comment if formatName
        else:
            abstract = entry.summary
            author = "Empty"

        if not abstract:
            abstract = "Empty"


    return title, journal_abb, date, author, abstract, graphical_abstract, url


#def formatName(authors_list, reverse=False):

    #"""Function to ormat the author's name in a specific way. Ex:
    #Jennifer A. Doudna -> J. A. Doudna"""
    #print(authors_list)

    ##New string to store all the authors, formatted
    #new_author = ""

    #for complete_name in authors_list:
        ##Example
        ##complete_name: Jennifer A. Doudna
        #complete_name = complete_name.replace("“", "")
        #complete_name = complete_name.split(" ")
        #person = ""

        #for piece_name in complete_name:
            #if piece_name is not complete_name[-1]:

                ##If the piece is already an abb, add directly
                #if "." in piece_name and len(piece_name) is 2:
                    #person += piece_name
                #else:
                    #person = person + piece_name[0] + "."
                #person += " "

            #else:
                #person += piece_name

        ##Add to the new_author string
        #if not new_author:
            #new_author += person
        #else:
            #new_author = new_author + ", " + person

    #return new_author


def getDoi(journal, entry):

    """Get the DOI number of a post, to save time"""

    rsc, _ = getJournals("rsc")
    acs, _ = getJournals("acs")
    wiley, _ = getJournals("wiley")
    npg, _ = getJournals("npg")
    science, _ = getJournals("science")

    if journal in rsc:
        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("div")
        try:
            doi = r[0].text.split("DOI: ")[1].split(",")[0]
        except IndexError:
            doi = r[1].text.split("DOI:")[1].split(",")[0]

    if journal in wiley:
        doi = entry.prism_doi

    if journal in acs:
        doi = entry.id.split("dx.doi.org/")[1]

    if journal in npg:
        doi = entry.prism_doi

    if journal in science:
        doi = entry.dc_identifier

    doi = doi.replace(" ", "")

    return doi


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

        page = requests.get(url, timeout=20, headers=headers)

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

        elif page.status_code != requests.codes.ok:
            print("Bad return code: {0}".format(page.status_code))
            return "wrongPage", None

    except requests.exceptions.Timeout:
        print("downloadPic, timeout")
        return "timeOut", None
    except Exception as e:
        print("toujours")
        print(e)


def getJournals(company):

    """Function to get the journal name and its abbreviation"""

    names = []
    abb = []

    with open('journals/{0}.ini'.format(company), 'r') as config:
        for line in config:
            names.append(line.split(" : ")[0])
            abb.append(line.split(" : ")[1].replace("\n", ""))

    return names, abb



if __name__ == "__main__":

    #urls_test = ["ang.xml"]
    #urls_test = ["jacs.xml"]
    #urls_test = ["http://feeds.rsc.org/rss/nj"]
    #urls_test = ["njc.xml"]
    #urls_test = ["http://feeds.rsc.org/rss/sc"]
    urls_test = ["science.xml"]

    for site in urls_test:

        feed = feedparser.parse(site)

        #print(feed)

        #Name of the journal
        journal = feed['feed']['title'] 

        print(journal)

        for entry in feed.entries:
            #print(entry.title)
            getData(journal, entry)
            #print("\n")
            #break

        #print("\n\n")

