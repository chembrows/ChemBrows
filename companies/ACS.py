#!/usr/bin/python
# coding: utf-8

import os
import sys
import feedparser

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

    def get_doi(entry: feedparser.util.FeedParserDict) -> str:

        doi = entry.id.split("dx.doi.org/")[1]

        return doi


if __name__ == '__main__':
    company_obj = CompanyHandler("http://feeds.feedburner.com/acs/jcisd8")
    pass
