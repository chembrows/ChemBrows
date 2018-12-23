#!/usr/bin/python
# coding: utf-8

import os
import sys
import feedparser
import arrow
from time import mktime
from bs4 import BeautifulSoup as BS
from bs4 import SoupStrainer as SS
import requests


sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from log import MyLog
from base_company import BaseCompany


class CompanyHandler(BaseCompany):

    def __init__(self, url: str) -> None:

        self.l = MyLog("activity.log")
        self.url = url

    def get_doi(self, entry: feedparser.util.FeedParserDict) -> str:

        doi = entry.id.split("dx.doi.org/")[1]

        return doi

    def refine_url(self, entry: feedparser.util.FeedParserDict):

        url = getattr(entry, 'feedburner_origlink', entry.link)
        id_paper = url.split('/')[-1]
        url = "https://pubs.acs.org/doi/abs/10.1021/" + id_paper

    def get_data(self, entry: feedparser.util.FeedParserDict, response=None):

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

        soup = BS(entry.summary, "html.parser")
        r = soup("img", alt="TOC Graphic")
        if r:
            graphical_abstract = r[0]['src']

        # If the dl went wrong, print an error
        if response.status_code is requests.codes.ok:

            strainer = SS("p", attrs={"class": "articleBody_abstractText"})
            soup = BS(response.text, "html.parser", parse_only=strainer)
            r = soup.p
            if r is not None:
                abstract = r.renderContents().decode()

            strainer = SS("h1", attrs={"class": "articleTitle"})
            soup = BS(response.text, "html.parser", parse_only=strainer)
            r = soup.h1
            if r is not None:
                title = r.renderContents().decode()


if __name__ == '__main__':
    company_obj = CompanyHandler("http://feeds.feedburner.com/acs/jcisd8")
    pass
