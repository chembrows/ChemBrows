#!/usr/bin/python
# -*-coding:Utf-8 -*

import feedparser
from bs4 import BeautifulSoup
import requests
import arrow
from time import mktime

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
    elsevier, elsevier_abb, _ = getJournals("elsevier")
    thieme, thieme_abb, _ = getJournals("thieme")
    beil, beil_abb, _ = getJournals("beilstein")

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
        author = None

        soup = BeautifulSoup(entry.summary)

        r = soup.find_all("img", align="center")
        if r:
            graphical_abstract = r[0]['src']

        if response.status_code is requests.codes.ok:
            soup = BeautifulSoup(response.text)

            # Get the title (w/ html)
            title = soup("h2", attrs={"class": "alpH1"})
            if title:
                title = title[0].renderContents().decode().lstrip().rstrip()

            # Get the abstrat (w/ html)
            r = soup.find_all("p", xmlns="http://www.rsc.org/schema/rscart38")
            if r:
                abstract = r[0].renderContents().decode()
                if abstract == "":
                    abstract = None

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

        abstract = soup.renderContents().decode()

        if abstract == "":
            abstract = None

        r = soup.find_all("a", attrs={"class": "figZoom"})
        if r:
            # answer, graphical_abstract = downloadPic(r[0]['href'])
            graphical_abstract = r[0]['href']
            r[0].replaceWith("")

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

    elif journal in elsevier:

        title = entry.title
        journal_abb = elsevier_abb[elsevier.index(journal)]
        # date = entry.updated_parsed
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        url = entry.id

        graphical_abstract = None
        author = None

        abstract = entry.summary

        # TODO: utiliser renderContents
        if abstract:
            try:
                author = abstract.split("Author(s): ")[1].split("<br")[0].split("<")[0]
                author = author.replace(" , ", ", ")
                author = author.replace("  ", " ")
            except IndexError:
                author = None

            soup = BeautifulSoup(abstract)
            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']

            try:
                abstract = abstract.split("<br />")[3].lstrip()
            except IndexError:
                abstract = ""

            if abstract == "":
                abstract = None


    elif journal in thieme:

        title = entry.title
        journal_abb = thieme_abb[thieme.index(journal)]
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        url = entry.id

        abstract = None
        graphical_abstract = None
        author = None

        if response.status_code is requests.codes.ok:

            soup = BeautifulSoup(response.text)

            if entry.summary != "":
                abstract = soup("section", id="abstract")[0]
                abstract("div", attrs={"class": "articleFunctions"})[0].extract()
                [tag.extract() for tag in soup("a", attrs={"name": True})]

                try:
                    abstract("div", attrs={"class": "articleKeywords"})[0].extract()
                except IndexError:
                    pass

                abstract = abstract.renderContents().decode()

            r = soup.find_all("span", id="authorlist")
            if r:
                author = r[0].text
                author = author.replace("*a, b", "")
                author = author.replace("*a", "")
                author = author.replace("*", "")


    elif journal in beil:

        title = entry.title
        journal_abb = beil_abb[beil.index(journal)]
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')
        url = entry.link

        abstract = None
        graphical_abstract = None
        author = None

        if entry.summary != "":
            soup = BeautifulSoup(entry.summary)
            abstract = [tag.renderContents().decode() for tag in soup("p")[:-2]]
            abstract = "".join(abstract)
            print(abstract)
            # graphical_abstract = soup("p")[-2]
            # abstract = entry.content[0].value
            # abstract = abstract.split("<br />")[3]

        # soup = BeautifulSoup(entry.content[0].value)
        # r = soup.find_all("img")
        # if r:
            # graphical_abstract = r[0]['src']
        # print(abstract)
        # print(graphical_abstract)

    else:
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
    elsevier = getJournals("elsevier")[0]
    thieme = getJournals("thieme")[0]
    beil = getJournals("beilstein")[0]

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

    # FUCK !! for this published, the doi is not given
    # in the RSS flux. It's so replaced by the url
    elif journal in elsevier:
        doi = entry.id

    elif journal in thieme:
        doi = entry.prism_doi

    try:
        doi = doi.replace(" ", "")
    except UnboundLocalError:
        # print("Erreur in getDoi: {0}".format(journal))
        return None

    return doi


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
        # print(abstract)
        # print(authors)
        # print(title)

    # urls_test = ["debug/bel.xml"]
    # urls_test = ["debug/syn.xml"]
    urls_test = ["debug/njc.htm"]

    session = FuturesSession(max_workers=50)

    list_urls = []

    feed = feedparser.parse(urls_test[0])
    journal = feed['feed']['title']

    print(journal)

    for entry in feed.entries:
        url = entry.link
        title = entry.title
        # if title != "Three-dimensional graphene hydrogel supported ultrafine RuO2 nanoparticles for supercapacitor electrodes":
            # continue
        # print(entry)
        # print(url)
        # print(title)
        future = session.get(url)
        future.add_done_callback(functools.partial(print_result, journal, entry))
        # break
