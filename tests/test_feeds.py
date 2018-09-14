#!/usr/bin/python
# coding: utf-8


"""
Test module to be ran with pytest.

Start the tests with something like this:
py.test -xs test_hosts.py -k getData
"""


import os
import requests
import pytest
import validators
from bs4 import BeautifulSoup, SoupStrainer

from log import MyLog

# Nbr of ACS journals registered
NBR_ACS_JOURNALS = 55


l = MyLog("output_tests_feeds.log", mode='w')
l.debug("---------------------- START NEW RUN OF TESTS ----------------------")


def logAssert(test, msg):

    """Function to log the result of an assert
    http://stackoverflow.com/questions/24892396/py-test-logging-messages-and-test-results-assertions-into-a-single-file
    """

    if not test:
        l.error(msg)
        assert test, msg


def test_ACSFeeds():

    """Function to test we have the right number of ACS journals"""

    page = requests.get("http://pubs.acs.org/page/follow.html", timeout=60)

    if page.status_code is not requests.codes.ok:
        pytest.fail("Failed to download ACS journals page")

    # Strainer: get a soup with only the interesting part.
    # Don't load the complete tree in memory. Saves RAM
    strainer = SoupStrainer("div", attrs={"id": "follow-pane-rss"})
    soup = BeautifulSoup(page.text, "html.parser", parse_only=strainer)
    r = soup.find_all("li")

    dic_journals = {}

    # Exclude some feeds that are not journals
    exclude = ["http://pubs.acs.org/editorschoice/feed/rss",
               "http://feeds.feedburner.com/AnalyticalChemistryA-pages",
               "http://feeds.feedburner.com/cen_latestnews",
               "http://feeds.feedburner.com/EnvironmentalScienceTechnologyOnlineNews",
               "http://feeds.feedburner.com/JournalOfProteomeResearch"
               ]

    for element in r:
        # print(element)

        url = element.a['href']

        if 'feed' in url and url not in exclude:
            name = element.text.strip()
            # print(name)
            # print("{} : {}".format(name, url))
            dic_journals[url] = name

    print(dic_journals)
    logAssert(len(dic_journals) == NBR_ACS_JOURNALS,
              "Wrong number of ACS journals: {} instead of {}".
              format(NBR_ACS_JOURNALS, len(dic_journals.values())))


if __name__ == "__main__":
    test_ACSFeeds()
