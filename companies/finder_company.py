#!/usr/bin/python
# coding: utf-8

import os
import sys
import feedparser
from typing import Dict

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from exceptions import *
from log import MyLog
import functions
from companies.base_company import BaseCompany


class FinderCompany:

    # Set the timeout for the futures
    # W/ a large timeout, less chances to get en exception
    TIMEOUT = 20

    def __init__(self, url_feed: str) -> None:

        self.l = MyLog("activity.log")
        self.l.debug("Entering CompanyBase")

        self.url_feed = url_feed

    def init_feed(self) -> None:

        try:
            # Get the RSS page of the url provided
            self.feed = feedparser.parse(self.url_feed, timeout=self.TIMEOUT)

            self.l.debug("RSS page successfully dled")

        except Exception as e:
            self.l.error(
                f"RSS page {self.url_feed} could not be downloaded: {e}", exc_info=True
            )

            raise DownloadError(f"Couldn't download feed {self.url_feed}")

    def init_infos(self, dict_journals: Dict[str, tuple]) -> None:

        try:
            # Check if the feed has a title (journal's name)
            self.journal = self.feed["feed"]["title"]
        except Exception as e:
            self.l.error(
                f"Unidentified journal for URL {self.url_feed}: {e}", exc_info=True
            )
            raise JournalError(f"Journal not recognized for {self.url_feed}")

        # Get the company and the journal_abb from the dictionary built in the main
        # window object. avoid multiple calls to hosts.getJournals and race conditions
        # care_image determines if the Worker will try to dl the graphical abstracts
        for abbreviation, tuple_data in dict_journals.items():
            if self.journal == tuple_data[1]:
                self.company, _, _, care_image = tuple_data
                self.journal_abb = abbreviation
                break

    def find_company_handler(self) -> BaseCompany:

        resource_dir, _ = functions.getRightDirs()
        directory = os.path.join(resource_dir, "companies")

        # Add module's directory to the import path
        sys.path.insert(0, directory)

        module = __import__(self.company)
        company_handler = module.CompanyHandler()

        return company_handler


if __name__ == "__main__":
    import hosts

    company_obj = FinderCompany("http://feeds.feedburner.com/acs/jcisd8")
    company_obj.init_feed()
    company_obj.init_infos(hosts.createDictJournals())
    company_obj.find_company_handler()
    pass
