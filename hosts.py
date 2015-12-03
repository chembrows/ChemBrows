#!/usr/bin/python
# coding: utf-8


import os, sys
import feedparser
from bs4 import BeautifulSoup, SoupStrainer
import requests
import arrow
from time import mktime
import re

# DEBUG
# from memory_profiler import profile

# Personal modules
import functions


def reject(entry_title):

    """Function called by a Worker object to filter crappy entries.
    It is meant to reject articles like corrigendum, erratum, etc"""

    if getattr(sys, "frozen", False):
        resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        resource_dir = '.'

    # resource_dir = os.path.dirname(os.path.dirname(sys.executable))
    # Load the regex stored in a config file, as filters
    with open(os.path.join(resource_dir, 'config/regex.txt'), 'r') as filters_file:
        filters = filters_file.read().splitlines()

    # Try to match the filters against the title entry
    responses = [bool(re.search(regex, entry_title)) for regex in filters]

    # If one filter matched, reject the entry
    if True in responses:
        return True
    else:
        return False


def updateData(company, journal, entry, care_image):

    """Function called by a Worker object when an RSS entry is
    not in list_ok. The entry has so to be updated. This function
    deals w/ the update, trough 2 booleans. If dl_image is True,
    the Worker will try to dl the image, w/ the URL returned by this
    function. If dl_page is True, the Worker will dl the article's page,
    AND will try to dl the image anyway, trough the futures mechanism of
    the worker"""

    dl_image = True
    dl_page = True
    graphical_abstract = None

    # NOTE:
    # company = 'npg' is not mentionned, but dl_image & dl_page are True

    # TODO: npg2

    if company == 'rsc':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("img", align="center")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'wiley':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("a", attrs={"class": "figZoom"})
        if r:
            graphical_abstract = r[0].extract()
            graphical_abstract = graphical_abstract['href']


    elif company == 'acs':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("img", alt="TOC Graphic")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'nas':
        dl_page = False


    elif company == 'science':
        dl_page = False


    elif company == 'elsevier':
        dl_page = False

        if entry.summary != "":
            soup = BeautifulSoup(entry.summary)
            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']


    elif company == 'beilstein':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("img")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'thieme':
        dl_page = False


    else:
        pass

    if graphical_abstract is None:
        dl_image = False

    return dl_page, dl_image, {'graphical_abstract': graphical_abstract}



# @profile
def getData(company, journal, entry, response=None):

    """Get the data. Starts from the data contained in the RSS flux, and if
    necessary, parse the website for supplementary infos. Download the
    graphical abstract"""

    # If the journal is edited by the RSC
    if company == 'rsc':

        """Graphical abstract present in RSS. Abstract incomplete
        and w/out html. Title w/out html"""

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

        url = getattr(entry, 'feedburner_origlink', entry.link)

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

        """Feed compltete. Abstract w/ html. Title w/out html"""

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
                    title = r.renderContents().decode().strip()
                except IndexError:
                    title = r.renderContents().decode().strip()


    elif company == 'acs':

        """Feed only contains graphical abstract"""

        title = entry.title.rstrip()
        date = arrow.get(entry.updated).format('YYYY-MM-DD')
        abstract = None

        author = entry.author
        author = entry.author.split(" and ")
        if len(author) > 1:
            author = ", ".join(author)
        else:
            author = author[0]

        url = getattr(entry, 'feedburner_origlink', entry.link)

        graphical_abstract = None

        soup = BeautifulSoup(entry.summary)
        r = soup("img", alt="TOC Graphic")
        if r:
            graphical_abstract = r[0]['src']

        # If the dl went wrong, print an error
        if response.status_code is requests.codes.ok:

            strainer = SoupStrainer("p", attrs={"class": "articleBody_abstractText"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.p
            if r is not None:
                abstract = r.renderContents().decode()

            strainer = SoupStrainer("h1", attrs={"class": "articleTitle"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()


    elif company == 'npg':

        title = entry.title
        date = entry.date
        abstract = entry.summary
        graphical_abstract = None

        url = entry.links[0]['href']

        try:
            author = [dic['name'] for dic in entry.authors]
            if author:
                if len(author) > 1:
                    author = ", ".join(author)
                else:
                    author = author[0]
            else:
                author = None
        except AttributeError:
            author = None


        if response.status_code is requests.codes.ok or response.status_code == 401:

            strainer = SoupStrainer("h1", attrs={"class": "article-heading"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()

            strainer = SoupStrainer("div", attrs={"id": "first-paragraph"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.div
            if r is not None:
                abstract = r.renderContents().decode()

            strainer = SoupStrainer("figure")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            # r = soup.find_all("img", attrs={"class": "fig"})
            # r = soup.find_all("img", attrs={"class": "fig carousel-item"})
            r = soup.find_all("img")
            if r:
                graphical_abstract = "http://www.nature.com" + r[0]["src"]

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

                try:
                    author = entry.summary.split("Author: ")[1]
                except IndexError:
                    pass
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

        abstract = None

        if response.status_code is requests.codes.ok:

            # Get the correct title, not the one in the RSS
            strainer = SoupStrainer("h1", id="article-title-1")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("h1", id="article-title-1")
            if r:
                title = r[0].renderContents().decode()

            # Get the authors
            strainer = SoupStrainer("a", attrs={"class": "name-search"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("a", attrs={"class": "name-search"})
            if r:
                author = [tag.text for tag in r]
                author = ", ".join(author)

            # Try to get the complete abstract. Sometimes it's available, sometimes
            # the article only contains an extract
            strainer = SoupStrainer("div", attrs={"class": "section abstract"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            if soup.p is not None:
                abstract = soup.p.renderContents().decode()
            else:
                abstract = entry.summary


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


    elif company == 'beilstein':

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
                # This company can change the background of the GA through
                # the url. If nothing is done, the bg is black, so turn it
                # to white. Doesn't affect images with unchangeable bg
                graphical_abstract = r[0]['src'] + '&background=FFFFFF'


    elif company == 'npg2':

        title = entry.title
        date = entry.date
        abstract = entry.summary
        graphical_abstract = None

        url = entry.links[0]['href']

        try:
            author = [dic['name'] for dic in entry.authors]
            if author:
                if len(author) > 1:
                    author = ", ".join(author)
                else:
                    author = author[0]
            else:
                author = None
        except AttributeError:
            author = None

        if response.status_code is requests.codes.ok or response.status_code == 401:

            strainer = SoupStrainer("h1", attrs={"class": "tighten-line-height small-space-below"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()

            strainer = SoupStrainer("div", attrs={"id": "abstract-content"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.p
            if r is not None:
                abstract = r.renderContents().decode()

            strainer = SoupStrainer("img")
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("img", attrs={"alt": "Figure 1"})
            if r:
                if "f1.jpg" in r[0]["src"]:
                    graphical_abstract = "http://www.nature.com" + r[0]["src"]

    else:
        return None


    if abstract is not None:
        topic_simple = " " + functions.simpleChar(BeautifulSoup(abstract).text) + functions.simpleChar(title) + " "
    else:
        topic_simple = " " + functions.simpleChar(title) + " "

    if abstract is None or abstract == '':
        abstract = "Empty"
    if graphical_abstract is None:
        graphical_abstract = "Empty"
    if author is None or author == '':
        author = "Empty"


    return title, date, author, abstract, graphical_abstract, url, topic_simple


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

    elif company == 'npg' or company == 'npg2':
        doi = entry.prism_doi

    elif company == 'science':
        doi = entry.dc_identifier

    elif company == 'nas':
        base = entry.dc_identifier
        base = base.split("pnas;")[1]
        doi = "10.1073/pnas." + base

    # FUCK !! for this publisher, the doi is not given
    # in the RSS flux. It's so replaced by the url
    elif company == 'elsevier':
        doi = entry.id

    elif company == 'thieme':
        doi = entry.prism_doi

    elif company == 'beilstein':
        doi = entry.summary.split("doi:")[1].split("</p>")[0]

    try:
        doi = doi.replace(" ", "")
    except UnboundLocalError:
        print("Erreur in getDoi: {0}".format(journal))
        return None

    return doi


def getJournals(company):

    """Function to get the informations about all the journals of
    a company. Returns the names, the URLs, the abbreviations, and also
    a boolean to set the download of the graphical abstracts. If for a
    journal this boolean is False, the Worker object will not try to dl
    the picture"""

    names = []
    abb = []
    urls = []
    cares_image = []

    if getattr(sys, "frozen", False):
        resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        resource_dir = '.'

    with open(os.path.join(resource_dir, 'journals/{0}.ini'.format(company)), 'r') as config:
        for line in config:
            names.append(line.split(" : ")[0])
            abb.append(line.split(" : ")[1].rstrip())
            urls.append(line.split(" : ")[2].rstrip())

            # Get a bool: care about the image when refreshing
            try:
                care = line.split(" : ")[3].rstrip()
                if care == "False":
                    cares_image.append(False)
                else:
                    cares_image.append(True)
            except IndexError:
                cares_image.append(True)

    return names, abb, urls, cares_image



if __name__ == "__main__":

    from requests_futures.sessions import FuturesSession
    import functools

    def print_result(journal, entry, future):
        response = future.result()
        title, date, authors, abstract, graphical_abstract, url, topic_simple = getData("npg", journal, entry, response)
        # print(abstract)
        # print("\n")
        print(graphical_abstract)
        # print("\n")
        # print(authors)
        # print("\n")
        # print(title)
        # print("\n")

    # urls_test = ["debug/lett.xht"]
    urls_test = ["http://feeds.nature.com/nmeth/rss/aop?format=xml"]

    session = FuturesSession(max_workers=20)

    list_urls = []

    feed = feedparser.parse(urls_test[0])
    journal = feed['feed']['title']

    # headers = {'User-agent': 'Mozilla/5.0',
               # 'Connection': 'close'}

    headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
               'Connection': 'close'}


    print(journal)

    for entry in feed.entries:
        url = entry.link
        # print(entry)

        # print(entry.title)

        print(url)

        # url = entry.feedburner_origlink
        # title = entry.title

        # if "cross reactive" not in title:
            # continue
        # title = entry.title

        # if "cross reactive" not in title:
            # continue
        # print(url)
        # print(title)
        # print(entry)
        # print(url)
        # getDoi(journal, entry)

        future = session.get(url, headers=headers, timeout=20)
        future.add_done_callback(functools.partial(print_result, journal, entry))

        break
