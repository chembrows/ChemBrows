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


l = MyLog("output_tests.log", mode='w')
l.debug("---------------------- START NEW RUN OF TESTS ----------------------")


def logAssert(test, msg):

    """Function to log the result of an assert
    http://stackoverflow.com/questions/24892396/py-test-logging-messages-and-test-results-assertions-into-a-single-file
    """

    if not test:
        l.error(msg)
        assert test, msg


def test_ACSFeeds():

    page = requests.get("http://pubs.acs.org/page/follow.html")
    # # Get the title (w/ html)
    # Strainer: get a soup with only the interesting part.
    # Don't load the complete tree in memory. Saves RAM
    strainer = SoupStrainer("ul", attrs={"class": "feeds"})
    soup = BeautifulSoup(page.text, parse_only=strainer)

    r = soup.find_all("li")

    for element in r:

        url = element.a['href']

        if 'feed' in url:
            print("{} : {}".format(element.text.strip(), url))

if __name__ == "__main__":
    test_ACSFeeds()
