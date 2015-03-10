#!/usr/bin/python
# -*-coding:Utf-8 -*

# import sys
# import os
import feedparser
from bs4 import BeautifulSoup
import requests
# from io import open as iopen
import arrow

# TEST
import re

# Personal modules
import functions


def getData(journal, entry, response=None):

    """Get the data. Starts from the data contained in the RSS flux, and if necessary,
    parse the website for supplementary infos. Download the graphical abstract"""

    # This function is called like this in parse.py:
    # title, date, authors, abstract, graphical_abstract = hosts.getData(journal, entry)

    # List of the journals
    rsc, rsc_abb, _ = getJournals("rsc")
    acs, acs_abb, _ = getJournals("acs")
    wiley, wiley_abb, _ = getJournals("wiley")
    npg, npg_abb, _ = getJournals("npg")
    science, science_abb, _ = getJournals("science")
    nas, nas_abb, _ = getJournals("nas")

    # If the journal is edited by the RSC
    if journal in rsc:

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        journal_abb = rsc_abb[rsc.index(journal)]

        try:
            url = entry.feedburner_origlink
        except AttributeError:
            url = entry.link

        abstract = None
        graphical_abstract = None

        soup = BeautifulSoup(entry.summary)

        r = soup.find_all("div")

        author = None

        graphical_abstract = r[0].img
        if graphical_abstract is not None:
            graphical_abstract = r[0].img['src']

        if response.status_code is requests.codes.ok:
            # Get the abstract
            soup = BeautifulSoup(response.text)
            r = soup.find_all("meta", attrs={"name": "citation_abstract"})
            if r:
                abstract = r[0]['content']

            r = soup.find_all("meta", attrs={"name": "citation_author"})
            if r:
                author = [tag['content'] for tag in r]
                author = ", ".join(author)


    elif journal in wiley:

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
            # answer, graphical_abstract = downloadPic(r[0]['href'])
            graphical_abstract = r[0]['href']
            r[0].replaceWith("")
            abstract = soup.renderContents().decode()


    elif journal in acs:

        title = entry.title.replace("\n", " ")
        journal_abb = acs_abb[acs.index(journal)]
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        abstract = None

        # If there is only one author
        try:
            author = entry.author.split(" and ")
            author = author[0] + ", " + author[1]
            author = author.split(", ")
            author = ", ".join(author)
        except IndexError:
            author = entry.author

        try:
            url = entry.feedburner_origlink
        except AttributeError:
            url = entry.link

        graphical_abstract = None

        # If the dl went wrong, print an error
        if response.status_code is requests.codes.ok:
            soup = BeautifulSoup(response.text)
            r = soup.find_all("p", attrs={"class": "articleBody_abstractText"})
            if r:
                abstract = r[0].text

            soup = BeautifulSoup(entry.summary)
            r = soup.find_all("img", alt="TOC Graphic")
            if r:
                graphical_abstract = r[0]['src']


    elif journal in npg:

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

        # If the dl went wrong, print an error
        if response.status_code is requests.codes.ok:
            soup = BeautifulSoup(response.text)
            r = soup.find_all("img", attrs={"class": "fig"})

            if r:
                if "f1.jpg" in r[0]["src"]:
                    graphical_abstract ="http://www.nature.com" + r[0]["src"]

                    if "carousel" in graphical_abstract:
                        graphical_abstract = graphical_abstract.replace("carousel", "images_article")

    elif journal in science:

        title = entry.title
        journal_abb = science_abb[science.index(journal)]
        date = entry.date
        url = entry.id

        graphical_abstract = None
        author = None

        abstract = entry.summary

        if not abstract:
            abstract = None
        else:
            if "Author:" in entry.summary:
                abstract = entry.summary.split("Author: ")[0]
                author = entry.summary.split("Author: ")[1]
            elif "Authors:" in entry.summary:
                abstract = entry.summary.split("Authors: ")[0]
                author = entry.summary.split("Authors: ")[1].split(", ")
                author = ", ".join(author)  # To comment if formatName


    elif journal in nas:

        title = entry.title
        journal_abb = nas_abb[nas.index(journal)]
        date = entry.prism_publicationdate
        url = entry.id

        graphical_abstract = None
        author = None

        abstract = entry.summary

        if response.status_code is requests.codes.ok:
            # Get the abstract
            soup = BeautifulSoup(response.text)

            # Get the correct title, no the one in the RSS
            r = soup.find_all("h1", id="article-title-1")
            if r:
                title = r[0].text
            # print(soup)
            # r = soup.find_all("p", id=re.compile("p-[1-9]"))
            # string = [tag.text for tag in r]
            # string = " ".join(string)
            # string = " ".join(string.split())
            # print(string)

            # Get the authors
            r = soup.find_all("a", attrs={"class": "name-search"})
            if r:
                author = [tag.text for tag in r]
                author = ", ".join(author)

    else:
        print("Error: journal not identified")
        return None


    if abstract is not None:
        topic_simple = " " + functions.simpleChar(BeautifulSoup(abstract).text) + functions.simpleChar(title) + " "
    else:
        topic_simple = " " + functions.simpleChar(title) + " "

    if abstract is None:
        abstract = "Empty"
    if graphical_abstract is None:
        graphical_abstract = "Empty"
    if author is None:
        author = "Empty"

    return title, journal_abb, date, author, abstract, graphical_abstract, url, topic_simple


# def formatName(authors_list, reverse=False):

    # """Function to ormat the author's name in a specific way. Ex:
    # Jennifer A. Doudna -> J. A. Doudna"""
    # print(authors_list)

    # # New string to store all the authors, formatted
    # new_author = ""

    # for complete_name in authors_list:
        # # Example
        # # complete_name: Jennifer A. Doudna
        # complete_name = complete_name.replace("“", "")
        # complete_name = complete_name.split(" ")
        # person = ""

        # for piece_name in complete_name:
            # if piece_name is not complete_name[-1]:

                # # If the piece is already an abb, add directly
                # if "." in piece_name and len(piece_name) is 2:
                    # person += piece_name
                # else:
                    # person = person + piece_name[0] + "."
                # person += " "

            # else:
                # person += piece_name

        # # Add to the new_author string
        # if not new_author:
            # new_author += person
        # else:
            # new_author = new_author + ", " + person

    # return new_author


def getDoi(journal, entry):

    """Get the DOI number of a post, to save time"""

    rsc = getJournals("rsc")[0]
    acs = getJournals("acs")[0]
    wiley = getJournals("wiley")[0]
    npg = getJournals("npg")[0]
    science = getJournals("science")[0]
    nas = getJournals("nas")[0]

    if journal in rsc:
        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("div")
        try:
            doi = r[0].text.split("DOI: ")[1].split(",")[0]
        except IndexError:
            doi = r[1].text.split("DOI:")[1].split(",")[0]

    elif journal in acs:
        doi = entry.id.split("dx.doi.org/")[1]

    elif journal in wiley:
        doi = entry.prism_doi

    elif journal in npg:
        doi = entry.prism_doi

    elif journal in science:
        doi = entry.dc_identifier

    elif journal in nas:
        base = entry.dc_identifier
        base = base.split("pnas;")[1]
        doi = "10.1073/pnas." + base

    try:
        doi = doi.replace(" ", "")
    except UnboundLocalError:
        print("Erreur in getDoi: {0}".format(journal))

    return doi


# def downloadPic(url):

    # """The parameter is a list. The function will be able to evolve"""

    # # On essaie de récupérer chaque page correspondant
    # # à chaque url, ac un timeout
    # try:
        # # On utilise un user-agent de browser,
        # # ds le cas où les hébergeurs bloquent les bots
        # headers = {'User-agent': 'Mozilla/5.0'}

        # # On rajoute l'url de base comme referer,
        # # car certains sites bloquent l'accès direct aux images
        # headers["Referer"] = url

        # page = requests.get(url, timeout=20, headers=headers)

        # # Si la page a bien été récupérée
        # if page.status_code == requests.codes.ok:

            # path = "./graphical_abstracts/"

            # # On enregistre la page
            # with iopen(path + functions.simpleChar(url), 'wb') as file:
                # file.write(page.content)
                # # l.debug("image ok")

                # # On sort True si on matche une des possibilités
                # # de l'url
                # return True, functions.simpleChar(url)

        # elif page.status_code != requests.codes.ok:
            # print("Bad return code: {0}".format(page.status_code))
            # return "wrongPage", None

    # except requests.exceptions.Timeout:
        # print("downloadPic, timeout")
        # return "timeOut", None
    # except Exception as e:
        # print("toujours")
        # print(e)


def getJournals(company):

    """Function to get the journal name and its abbreviation"""

    names = []
    abb = []
    urls = []

    with open('journals/{0}.ini'.format(company), 'r') as config:
        for line in config:
            names.append(line.split(" : ")[0])
            abb.append(line.split(" : ")[1].replace("\n", ""))
            urls.append(line.split(" : ")[2].replace("\n", ""))

    return names, abb, urls



if __name__ == "__main__":
    from requests_futures.sessions import FuturesSession
    import functools

    def print_result(journal, entry, future):
        response = future.result()
        title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = getData(journal, entry, response)
        print(authors)
        # print(title)


    # urls_test = ["debug/ang.xml"]
    urls_test = ["debug/pnas.xml"]
    # urls_test = ["http://feeds.rsc.org/rss/nj"]
    # urls_test = ["http://feeds.rsc.org/rss/sc"]
    # urls_test = ["debug/science.xml"]
    # urls_test = ["debug/med_chem.htm"]
    # urls_test = ["debug/sm.htm"]


    session = FuturesSession(max_workers=50)
    # session = FuturesSession()

    list_urls = []

    # for site in urls_test:

    feed = feedparser.parse(urls_test[0])
    journal = feed['feed']['title']
    # print(feed.entries[0:])

    for entry in feed.entries[1:]:
        url = entry.link
        title = entry.title
        if title != "Stress and telomere shortening in central India [Anthropology]":
            continue
        else:
            print(entry)
            # print(feed.entries.index(entry))
            # print(entry.id)
            future = session.get(url)
            future.add_done_callback(functools.partial(print_result, journal, entry))
            break
