#!/usr/bin/python
# -*-coding:Utf-8 -*

import feedparser
from bs4 import BeautifulSoup, SoupStrainer
import requests
import arrow
from time import mktime

# Personal modules
import functions


def getData(company, journal, entry, response=None):

    """Get the data. Starts from the data contained in the RSS flux, and if necessary,
    parse the website for supplementary infos. Download the graphical abstract"""

    # If the journal is edited by the RSC
    if company == 'rsc':

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

        try:
            url = entry.feedburner_origlink
        except AttributeError:
            url = entry.link

        abstract = None
        graphical_abstract = None
        author = None

        soup = BeautifulSoup(entry.summary)

        r = soup("img", align="center")
        if r:
            graphical_abstract = r[0]['src']

        if response.status_code is requests.codes.ok:

            # # Get the title (w/ html)
            # Strainer: get a soup with only the interesting part.
            # Don't load the complete tree in memory. Saves RAM
            strainer = SoupStrainer("h2", attrs={"class": "alpH1"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            title = soup.h2

            if title is not None:
                # title = title.renderContents().decode().lstrip().rstrip()
                title = title.renderContents().decode().strip()

            # # Get the abstrat (w/ html)
            strainer = SoupStrainer("p", xmlns="http://www.rsc.org/schema/rscart38")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.p

            if r is not None:
                abstract = r.renderContents().decode()
                if abstract == "":
                    abstract = None

            strainer = SoupStrainer("meta", attrs={"name": "citation_author"})
            soup = BeautifulSoup(response.text, parse_only=strainer)

            # Here, multiple tags (results) are expected, so perform
            # the search, even if the tree contains only the result
            r = soup("meta", attrs={"name": "citation_author"})
            if r:
                author = [tag['content'] for tag in r]
                author = ", ".join(author)


    elif company == 'wiley':

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

        author = entry.author

        url = entry.prism_url

        graphical_abstract = None

        abstract = None

        soup = BeautifulSoup(entry.summary)
        try:
            # Remove the title "Abstract" from the abstract
            soup("h3")[0].extract()
        except IndexError:
            pass
        r = soup("a", attrs={"class": "figZoom"})
        if r:
            # Define the graphical abstract by extracting it
            # (and deleting it) from the abstract
            graphical_abstract = r[0].extract()
            graphical_abstract = graphical_abstract['href']

        abstract = soup.renderContents().decode()

        if abstract == "":
            abstract = None

        if response.status_code is requests.codes.ok:
            # soup = BeautifulSoup(response.text)

            # # Get the title (w/ html)
            strainer = SoupStrainer("span", attrs={"class": "mainTitle"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.span
            if r is not None:
                try:
                    # Remove the sign for the supplementary infos
                    r("a", href="#nss")[0].extract()
                except IndexError:
                    pass

                # Remove the image representing a bond
                try:
                    r("img", alt="[BOND]")[0].replaceWith("-")
                    # title = r.renderContents().decode().lstrip().rstrip()
                    title = r.renderContents().decode().strip()
                except IndexError:
                    # title = r.renderContents().decode().lstrip().rstrip()
                    title = r.renderContents().decode().strip()

                # print(title)


    elif company == 'acs':

        title = entry.title.replace("\n", " ")
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        abstract = None

        author = entry.author
        author = entry.author.split(" and ")
        if len(author) > 1:
            author = ", ".join(author)
        else:
            author = author[0]

        try:
            url = entry.feedburner_origlink
        except AttributeError:
            url = entry.link

        graphical_abstract = None

        soup = BeautifulSoup(entry.summary)
        r = soup("img", alt="TOC Graphic")
        if r:
            graphical_abstract = r[0]['src']

        # If the dl went wrong, print an error
        if response.status_code is requests.codes.ok:
            # soup = BeautifulSoup(response.text)

            # r = soup("p", attrs={"class": "articleBody_abstractText"})
            strainer = SoupStrainer("p", attrs={"class": "articleBody_abstractText"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.p
            if r is not None:
                abstract = r.renderContents().decode()

            # r = soup("h1", attrs={"class": "articleTitle"})
            strainer = SoupStrainer("h1", attrs={"class": "articleTitle"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()


    elif company == 'npg':

        title = entry.title
        date = entry.date
        url = entry.link
        abstract = entry.summary
        graphical_abstract = None
        author = None

        if response.status_code is requests.codes.ok or response.status_code == 401:
            soup = BeautifulSoup(response.text)

            # r = soup.find_all("ul", attrs={"class": "authors citation-authors"})
            strainer = SoupStrainer("ul", attrs={"class": "authors citation-authors"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("ul", attrs={"class": "authors citation-authors"})
            if r:
                s = r[0].find_all("span", attrs={"class": "fn"})
                if s:
                    author = [tag.renderContents().decode() for tag in s]
                    author = ", ".join(author)

            # r = soup.find_all("h1", attrs={"class": "article-heading"})
            strainer = SoupStrainer("h1", attrs={"class": "article-heading"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()

            # r = soup.find_all("div", attrs={"id": "first-paragraph"})
            strainer = SoupStrainer("div", attrs={"id": "first-paragraph"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.div
            if r is not None:
                # [tag.extract() for tag in r[0]("a", title=True)]
                abstract = r.renderContents().decode()

            strainer = SoupStrainer("img")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("img", attrs={"class": "fig"})
            if r:
                if "f1.jpg" in r[0]["src"]:
                    graphical_abstract ="http://www.nature.com" + r[0]["src"]

                    if "carousel" in graphical_abstract:
                        graphical_abstract = graphical_abstract.replace("carousel", "images_article")


    elif company == 'science':

        title = entry.title
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


    elif company == 'nas':

        title = entry.title
        date = entry.prism_publicationdate
        url = entry.id

        graphical_abstract = None
        author = None

        abstract = entry.summary

        if response.status_code is requests.codes.ok:
            # Get the abstract
            # soup = BeautifulSoup(response.text)

            # Get the correct title, no the one in the RSS
            # r = soup.find_all("h1", id="article-title-1")
            strainer = SoupStrainer("h1", id="article-title-1")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("h1", id="article-title-1")
            if r:
                title = r[0].renderContents().decode()

            # Get the authors
            # r = soup.find_all("a", attrs={"class": "name-search"})
            strainer = SoupStrainer("a", attrs={"class": "name-search"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("a", attrs={"class": "name-search"})
            if r:
                author = [tag.text for tag in r]
                author = ", ".join(author)


    elif company == 'elsevier':

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        url = entry.id

        graphical_abstract = None
        author = None

        abstract = entry.summary

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

        # NOTE: javascript embedded, impossible
        # if response.status_code is requests.codes.ok:
            # url = response.url
            # print(response.url)
            # # Get the abstract
            # soup = BeautifulSoup(response.text)

            # Get the correct title, no the one in the RSS
            # r = soup.find_all("li", attrs={"class": "originalArticleName"})
            # print(r)
            # if r:
                # title = r[0].renderContents().decode()


    elif company == 'thieme':

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        url = entry.id

        abstract = None
        graphical_abstract = None
        author = None

        if response.status_code is requests.codes.ok:

            if entry.summary != "":

                # Get the abstract, and clean it
                strainer = SoupStrainer("section", id="abstract")
                soup = BeautifulSoup(response.text, parse_only=strainer)
                abstract = soup.section

                abstract("div", attrs={"class": "articleFunctions"})[0].extract()
                [tag.extract() for tag in abstract("a", attrs={"name": True})]
                [tag.extract() for tag in abstract("h3")]
                [tag.extract() for tag in abstract("ul", attrs={"class": "linkList"})]
                [tag.extract() for tag in abstract("a", attrs={"class": "gotolink"})]

                try:
                    abstract("div", attrs={"class": "articleKeywords"})[0].extract()
                except IndexError:
                    pass

                abstract = abstract.renderContents().decode()

            strainer = SoupStrainer("span", id="authorlist")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("span", id="authorlist")
            if r:
                author = r[0].text
                author = author.replace("*a, b", "")
                author = author.replace("*a", "")
                author = author.replace("*", "")


    elif company == 'beil':

        title = entry.title
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')
        url = entry.link

        abstract = None
        graphical_abstract = None

        author = entry.author
        author = entry.author.split(" and ")
        if len(author) > 1:
            author = ", ".join(author)
        else:
            author = author[0]

        if entry.summary != "":
            soup = BeautifulSoup(entry.summary)
            r = soup.find_all("p")

            if r:
                abstract = r[1].renderContents().decode()

            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']


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


    return title, date, author, abstract, graphical_abstract, url, topic_simple


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
            # if piece_name != complete_name[-1]:

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


def getDoi(company, journal, entry):

    """Get the DOI id of a post, to save time"""

    if company == 'rsc':
        soup = BeautifulSoup(entry.summary)
        r = soup("div")
        try:
            doi = r[0].text.split("DOI: ")[1].split(",")[0]
        except IndexError:
            doi = r[1].text.split("DOI:")[1].split(",")[0]

    elif company == 'acs':
        doi = entry.id.split("dx.doi.org/")[1]

    elif company == 'wiley':
        doi = entry.prism_doi

    elif company == 'npg':
        doi = entry.prism_doi

    elif company == 'science':
        doi = entry.dc_identifier

    elif company == 'nas':
        base = entry.dc_identifier
        base = base.split("pnas;")[1]
        doi = "10.1073/pnas." + base

    # FUCK !! for this published, the doi is not given
    # in the RSS flux. It's so replaced by the url
    elif company == 'elsevier':
        doi = entry.id

    elif company == 'thieme':
        doi = entry.prism_doi

    elif company == 'beil':
        doi = entry.summary.split("doi:")[1].split("</p>")[0]

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
    config.close()

    return names, abb, urls



if __name__ == "__main__":
    from requests_futures.sessions import FuturesSession
    import functools

    def print_result(journal, entry, future):
        response = future.result()
        title, date, authors, abstract, graphical_abstract, url, topic_simple = getData("npg", journal, entry, response)
        # print(abstract)
        # print(graphical_abstract)
        print(authors)
        # print(title)

    # urls_test = ["debug/rsc.htm"]
    # urls_test = ["debug/natcom.htm"]
    urls_test = ["debug/npg.htm"]

    session = FuturesSession(max_workers=20)

    list_urls = []

    feed = feedparser.parse(urls_test[0])
    journal = feed['feed']['title']

    headers = {'User-agent': 'Mozilla/5.0',
               'Connection': 'close'}


    print(journal)

    for entry in feed.entries:
        print(entry)
        # if "Ticket" not in entry.title:
            # continue
        # url = entry.link
        # url = entry.feedburner_origlink
        # title = entry.title
        # print(url)
        # print(title)
        # print(entry)
        # print(url)
        # getDoi(journal, entry)

        # future = session.get(url, headers=headers, timeout=20)
        # future.add_done_callback(functools.partial(print_result, journal, entry))

        break
