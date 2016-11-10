#!/usr/bin/python
# coding: utf-8


import os
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

    resource_dir, DATA_PATH = functions.getRightDirs()

    # resource_dir = os.path.dirname(os.path.dirname(sys.executable))
    # Load the regex stored in a config file, as filters
    with open(os.path.join(resource_dir, 'config/regex.txt'),
              'r') as filters_file:
        filters = filters_file.read().splitlines()

    # Try to match the filters against the title entry
    responses = [bool(re.search(regex, entry_title)) for regex in filters]

    # If one filter matched, reject the entry
    if True in responses:
        return True
    else:
        return False


def refineUrl(company, journal, entry):

    """Refine an URL to avoid redirections (speeds things up)"""

    url = getattr(entry, 'feedburner_origlink', entry.link)

    if company == 'ACS':
        id_paper = url.split('/')[-1]
        url = "http://pubs.acs.org/doi/abs/10.1021/" + id_paper

    elif company == 'Nature':
        id_paper = url.split('/')[-1]

        # Necessary. Sometimes the id has a point, sometimes not
        p = re.compile(r'[0-9.]')
        prefix = p.sub('', id_paper)

        url = "http://www.nature.com/{}/journal/vaop/ncurrent/abs/{}.html"
        url = url.format(prefix, id_paper)

    elif company == 'Nature2':
        id_paper = url.split('/')[-1].split('.')[0]
        url = "http://www.nature.com/articles/{}".format(id_paper)

    elif company == 'Wiley':
        # Optimization for Wiley
        doi = url.split('%2')[-1]
        url = "http://onlinelibrary.wiley.com/resolve/doi?DOI=10.1002%2F{}"
        url = url.format(doi)

    return url


def updateData(company, journal, entry, care_image):

    """Function called by a Worker object when an RSS entry is
    not in list_ok. The entry has so to be updated. This function
    deals w/ the update, trough 2 booleans. If dl_image is True,
    the Worker will try to dl the image, w/ the URL returned by this
    function. If dl_page is True, the Worker will dl the article's page,
    AND will try to dl the image anyway, trough the futures mechanism of
    the worker. care_image is not used right now, but might be one day"""

    dl_image = True
    dl_page = True
    graphical_abstract = None

    # NOTE:
    # Some companies are not mentionned, but dl_image & dl_page are True

    if company in ['Science', 'Thieme', 'PNAS']:
        dl_page = False

    elif company == 'RSC':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("img", align="center")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'Wiley':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("a", attrs={"class": "figZoom"})
        if r:
            graphical_abstract = r[0].extract()
            graphical_abstract = graphical_abstract['href']


    elif company == 'ACS':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup("img", alt="TOC Graphic")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'Elsevier':
        dl_page = False

        if entry.summary != "":
            soup = BeautifulSoup(entry.summary)
            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']


    elif company == 'Beilstein':
        dl_page = False

        soup = BeautifulSoup(entry.summary)
        r = soup.find_all("img")
        if r:
            graphical_abstract = r[0]['src']


    elif company == 'PLOS':
        dl_page = False

        base = "http://journals.plos.org/plosone/article/figure/image?size=medium&id=info:{}.g001"
        graphical_abstract = base.format(getDoi(company, journal, entry))


    else:
        pass

    if graphical_abstract is None:
        dl_image = False

    return dl_page, dl_image, {'graphical_abstract': graphical_abstract}


# @profile
def getData(company, journal, entry, response=None):

    """Get the data. Starts from the data contained in the RSS page and, if
    necessary, parses the website for additional information"""

    url = refineUrl(company, journal, entry)

    # If the journal is edited by the RSC
    if company == 'RSC':

        """Graphical abstract present in RSS. Abstract incomplete
        and w/out html. Title w/out html"""

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

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


    elif company == 'Wiley':

        """Feed compltete. Abstract w/ html. Title w/out html"""

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

        author = entry.author

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


    elif company == 'ACS':

        """Feed only contains graphical abstract"""

        title = entry.title.rstrip()
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')
        abstract = None

        author = entry.author
        author = entry.author.split(" and ")
        if len(author) > 1:
            author = ", ".join(author)
        else:
            author = author[0]

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


    elif company == 'Nature':

        title = entry.title
        date = entry.date
        abstract = entry.summary
        graphical_abstract = None

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
            r = soup.find_all("img")
            if r:
                graphical_abstract = "http://www.nature.com" + r[0]["src"]

                if "carousel" in graphical_abstract:
                    graphical_abstract = graphical_abstract.replace("carousel", "images_article")


    elif company == 'Science':

        title = entry.title
        date = entry.date

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


    elif company == 'PNAS':

        title = entry.title
        date = entry.prism_publicationdate

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


    elif company == 'Elsevier':

        title = entry.title
        date = arrow.get(mktime(entry.updated_parsed)).format('YYYY-MM-DD')

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

            try:
                # First type of abstract formatting
                abstract = soup("simple-para")[0].renderContents().decode()
            except IndexError:
                try:
                    # Second type of abstract formatting
                    abstract = abstract.split("<br />")[3].lstrip()
                except IndexError:
                    abstract = None

            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']

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


    elif company == 'Thieme':

        title = entry.title
        date = arrow.get(entry.updated).format('YYYY-MM-DD')

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

            # Get author strainer
            strainer = SoupStrainer("span", id="authorlist")
            author = BeautifulSoup(response.text, parse_only=strainer).span

            # Clean supscripts
            [tag.extract() for tag in author("sup")]
            author = author.renderContents().decode()
            author = author.replace("*", "")


    elif company == 'Beilstein':

        title = entry.title
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')

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


    elif company == 'Nature2':

        title = entry.title
        date = entry.date
        abstract = entry.summary
        graphical_abstract = None


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


    elif company == 'PLOS':

        title = entry.title
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')

        if entry.authors:
            author = []
            for element in entry.authors:
                author.append(element['name'])
            author = ", ".join(author)
        else:
            author = None

        abstract = BeautifulSoup(entry.summary)

        # Clean the authors' names from the abstract
        r = abstract.find_all("p")
        if r and str(r[0]).startswith("<p>by "):
            abstract("p")[0].extract()

        try:
            abstract("img")[0].extract()
        except IndexError:
            pass

        abstract = abstract.renderContents().decode().strip()

        base = "http://journals.plos.org/plosone/article/figure/image?size=medium&id=info:doi/{}.g001"
        graphical_abstract = base.format(getDoi(company, journal, entry))


    elif company == 'Springer':

        title = entry.title
        date = arrow.get(mktime(entry.published_parsed)).format('YYYY-MM-DD')
        graphical_abstract = None
        author = None

        abstract = BeautifulSoup(entry.summary)

        try:
            _ = abstract("h3")[0].extract()
            # Remove the graphical abstract part from the abstract
            _ = abstract("span", attrs={"class": "a-plus-plus figure category-standard float-no id-figa"})[0].extract()
        except IndexError:
            pass

        abstract = abstract.renderContents().decode().strip()

        if response.status_code is requests.codes.ok:

            strainer = SoupStrainer("div", attrs={"class": "MediaObject"})
            soup = BeautifulSoup(response.text, parse_only=strainer)

            # For now, it's one shot: if the dl fails for the GA, there
            # won't be a retry. That's bc too little articles have GA
            r = soup.find_all("img")
            if r:
                graphical_abstract = r[0]['src']

            strainer = SoupStrainer("ul", attrs={"class": "AuthorNames"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.find_all("span", attrs={"class": "AuthorName"})
            if r:
                author = [tag.text for tag in r]
                author = ", ".join(author)

            strainer = SoupStrainer("h1", attrs={"class": "ArticleTitle"})
            soup = BeautifulSoup(response.text, parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()


    elif company == 'Taylor':

        title = entry.title
        date = arrow.get(mktime(entry.updated_parsed)).format('YYYY-MM-DD')
        graphical_abstract = None
        author = None
        abstract = None

        if entry.authors:
            author = []
            for element in entry.authors:
                author.append(element['name'])
            author = ", ".join(author)
        else:
            author = None

        if response.status_code is requests.codes.ok:

            strainer = SoupStrainer("div", attrs={"class": "col-md-2-3 "})
            soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()

            strainer = SoupStrainer("div", attrs={"class": "abstractSection abstractInFull"})
            soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)
            r = soup.p
            if r is not None:
                abstract = r.renderContents().decode()

            r = soup.find_all("img")
            if r:
                base = "http://www.tandfonline.com{}"
                graphical_abstract = base.format(r[0]['src'])


    else:
        return None


    if abstract is not None:

        topic_simple = " " + \
                       functions.simpleChar(BeautifulSoup(abstract).text) + \
                       " " + functions.simpleChar(title) + " "
    else:
        topic_simple = " " + functions.simpleChar(title) + " "

    if abstract is None or abstract == '':
        abstract = "Empty"
    if graphical_abstract is None:
        graphical_abstract = "Empty"


    if author is None or author == '':
        author = "Empty"
        author_simple = None
    else:
        # Clean author field
        author = author.replace('  ', ' ')
        author = author.replace(' ,', ',')
        author_simple = " " + functions.simpleChar(author) + " "

    return title, date, author, abstract, graphical_abstract, url, topic_simple, author_simple


def getDoi(company, journal, entry):

    """Get the DOI id of a post, to save time"""

    if company == 'RSC':
        soup = BeautifulSoup(entry.summary)
        r = soup("div")
        try:
            doi = r[0].text.split("DOI: ")[1].split(",")[0]
        except IndexError:
            doi = r[1].text.split("DOI:")[1].split(",")[0]

    elif company in ['Wiley', 'Nature', 'Nature2', 'Thieme', 'Taylor']:
        doi = entry.prism_doi

    elif company == 'ACS':
        doi = entry.id.split("dx.doi.org/")[1]

    elif company == 'Science':
        doi = entry.dc_identifier

    elif company == 'PNAS':
        base = entry.dc_identifier
        base = base.split("pnas;")[1]
        doi = "10.1073/pnas." + base

    # For this publisher, the doi is not given
    # in the RSS flux. It's so replaced by the url
    elif company == 'Elsevier':
        doi = entry.id

    elif company == 'Beilstein':
        doi = entry.summary.split("doi:")[1].split("</p>")[0]

    elif company == 'PLOS':
        doi = "10.1371/" + entry.id.split('/')[-1]

    elif company == 'Springer':
        doi = "10.1007/" + entry.id.split('/')[-1]

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

    resource_dir, DATA_PATH = functions.getRightDirs()

    with open(os.path.join(resource_dir, 'journals/{0}.ini'.
              format(company)), 'r') as config:
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

    # If the user didn't add a journal from this company, the file
    # won't exist, so exit
    if not os.path.exists(os.path.join(DATA_PATH, 'journals/{0}.ini'.
                                                  format(company))):
        return names, abb, urls, cares_image

    with open(os.path.join(DATA_PATH, 'journals/{0}.ini'.
              format(company)), 'r') as config:

        for line in config:
            url = line.split(" : ")[2].rstrip()

            if url not in urls:
                names.append(line.split(" : ")[0])
                abb.append(line.split(" : ")[1].rstrip())
                urls.append(url)

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


def getCompanies():

    """Get a list of all the companies. Will return a list of
    publishers, without .ini at the end"""

    resource_dir, DATA_PATH = functions.getRightDirs()

    list_companies = []

    # List companies on the program side
    for company in os.listdir(os.path.join(resource_dir, 'journals')):
        company = company.split('.')[0]
        list_companies.append(company)

    # List companies on the user side
    for company in os.listdir(os.path.join(DATA_PATH, 'journals')):
        company = company.split('.')[0]
        if company not in list_companies:
            list_companies.append(company)

    return list_companies



if __name__ == "__main__":

    # print(getJournals('Science'))

    from requests_futures.sessions import FuturesSession
    import functools
    from pprint import pprint
    import webbrowser

    def print_result(journal, entry, future):
        response = future.result()
        title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = getData("Thieme", journal, entry, response)
        # print("\n")
        # print(abstract)
        # print(date)
        # print("\n")
        print(title)
        print(authors)
        # print("\n")
        # print("\n")
        # print(graphical_abstract)
        # os.remove("graphical_abstracts/{0}".format(functions.simpleChar(graphical_abstract)))
        # print("\n")

    # urls_test = ["http://feeds.nature.com/nature/rss/aop"]
    # urls_test = ["debug/springer.xml"]
    urls_test = ["https://www.thieme-connect.de/rss/thieme/en/10.1055-s-00000083.xml"]

    session = FuturesSession(max_workers=20)

    list_urls = []

    feed = feedparser.parse(urls_test[0], timeout=20)
    # print(feed.entries)
    # print(feed)
    journal = feed['feed']['title']
    print(journal)

    # headers = {'User-agent': 'Mozilla/5.0',
               # 'Connection': 'close'}

    headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
               'Connection': 'close'}

    for entry in feed.entries[2:]:

        # pprint(entry)

        url = refineUrl("Thieme", journal, entry)

        print(url)

        # webbrowser.open(url, new=0, autoraise=True)

        # url = entry.feedburner_origlink
        # title = entry.title

        # title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = getData("Elsevier", journal, entry)

        # print(entry.summary)

        # print(title)

        # print(abstract)

        # if "Density Functional" not in entry.title:
            # continue

        # print(entry)

        # if "cross reactive" not in title:
            # continue
        # print(url)
        # print(title)
        # pprint(entry)
        # print(url)
        # getDoi(journal, entry)

        future = session.get(url, headers=headers, timeout=20)
        future.add_done_callback(functools.partial(print_result, journal, entry))

        break
