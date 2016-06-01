#!/usr/bin/python
# coding: utf-8


"""
Test module to be ran with pytest.
Tests that hosts.py returns correct values

Start the tests with something like this:
py.test -xs test_hosts.py -k getData
"""


import os
import feedparser
import requests
import pytest
import random
import arrow
import validators
import traceback
import datetime

import hosts
from log import MyLog

LENGTH_SAMPLE = 3

l = MyLog("output_tests.log", mode='w')
l.debug("---------------------- START NEW RUN OF TESTS ----------------------")


def logAssert(test, msg):

    """Function to log the result of an assert
    http://stackoverflow.com/questions/24892396/py-test-logging-messages-and-test-results-assertions-into-a-single-file
    """

    if not test:
        l.error(msg)
        assert test, msg


def test_getJournals():

    """Function to get the informations about all the journals of
    a company. Returns the names, the URLs, the abbreviations, and also
    a boolean to set the download of the graphical abstracts"""

    l.debug("Starting test getJournals")
    start_time = datetime.datetime.now()

    # Create a dictionnary w/ all the data concerning the journals
    # implemented in the program: names, abbreviations, urls
    dict_journals = {}
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        dict_journals[company] = hosts.getJournals(company)

    l.debug(dict_journals)

    for company, data in dict_journals.items():

        # data is a tuple: (list_journals_publisher,
                          # list_abb_journals_publisher,
                          # list_urls_publisher,
                          # list_bool
                         # )

        logAssert(type(data) == tuple, "data is not a tuple {}".format(data))

        # Check that all the fields in the tuple are
        # non empty lists
        for list_info_journals in data[:-1]:
            logAssert(type(list_info_journals) == list and list_info_journals,
                      "list_info_journals is missing or is not a list {}".
                      format(list_info_journals))

            # Check that all the elements in the list are
            # non empty strings
            for element in list_info_journals:
                logAssert(type(element) == str and element,
                          "element is not a string or is an empty string {}".
                          format(element))

        # Check the urls of the RSS pages
        for element in data[2]:
            logAssert(validators.url(element),
                      "One of the publisher's URL is not a URL".
                      format(element))

        # Check the list of booleans
        for element in data[3]:
            logAssert(type(element) == bool,
                      "One boolean is not really a boolean {}".
                      format(element))

    l.debug("Time spent in test_getJournals: {}".
            format(datetime.datetime.now() - start_time))


@pytest.fixture()
def journalsUrls():

    """Returns a combined list of urls.
    All the journals of all the companies.
    Specific to the tests, fixture"""

    urls = []
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        urls += hosts.getJournals(company)[2]

    return urls


def test_getData(journalsUrls):

    """Tests the function getData. For each journal of each company,
    tests LENGTH_SAMPLE entries"""

    l.debug("Starting test getData \n")
    start_time = datetime.datetime.now()

    # Returns a list of the urls of the feed pages
    list_urls_feed = journalsUrls

    # TODO: comment or uncomment
    # Bypass all companies but one
    # list_urls_feed = hosts.getJournals("npg")[2]

    # Build a dic with key: company
                     # value: journal name
    dict_journals = {}
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        dict_journals[company] = hosts.getJournals(company)[0]

    # All the journals are tested
    for site in list_urls_feed:

        l.info("Site {} of {} \n".format(list_urls_feed.index(site) + 1,
                                         len(list_urls_feed)))

        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        # Get the company name
        for publisher, data in dict_journals.items():
            if journal in data:
                company = publisher

        l.info(journal)

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests LENGTH_SAMPLE entries for a journal, not all of them
        for entry in samples:

            if company in ['science', 'elsevier', 'beilstein']:
                title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry)
            else:
                if company == 'acs':
                    url = getattr(entry, 'feedburner_origlink',
                                  entry.link).split('/')[-1]
                    url = "http://pubs.acs.org/doi/abs/10.1021/" + url
                elif company == 'npg':
                    url = getattr(entry, 'feedburner_origlink',
                                  entry.link).split('/')[-1]
                    url = "http://www.nature.com/nature/journal/vaop/ncurrent/abs/" + url + ".html"
                else:
                    url = getattr(entry, 'feedburner_origlink', entry.link)


                try:
                    response = requests.get(url, timeout=10)
                    title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry, response)
                except Exception as e:
                    l.error("A problem occured: {}, continue to next entry".
                            format(e))
                    l.error(traceback.format_exc())

            l.info(title)
            l.info(url)
            l.info(graphical_abstract)
            l.info(date)

            if response.history:
                l.debug("Request was redirected")
                for resp in response.history:
                    l.debug("Status code, URL: {}, {}".
                            format(resp.status_code, resp.url))
                l.debug("Final destination:")
                l.debug("Status code, URL: {}, {} \n".
                        format(resp.status_code, response.url))
            else:
                l.debug("Request was not redirected \n")


            # ------------------------ ASSERT SECTION -------------------------


            logAssert(type(abstract) == str and abstract,
                      "Abstract missing or not a string {}".format(abstract))

            logAssert(type(url) == str and url,
                      "URL is missing or is not a string {}".format(url))

            # Test if url is valid
            if url != 'Empty':
                logAssert(validators.url(url) is True,
                          "URL is a string but is not a URL {}".format(url))

            # For ACS and Nature, check if the URL is the abstract page's URL
            if company in ['acs', 'npg']:
                logAssert('abs' in url,
                          "company is {}, but URL doesn't contain 'abs' {}".
                          format(company, url))

            logAssert(type(graphical_abstract) == str and graphical_abstract,
                      "graphical_abstract is missing or not a string {}".
                      format(graphical_abstract))

            if graphical_abstract != 'Empty':
                logAssert(validators.url(graphical_abstract) is True,
                          "graphical_abstract is a string but is not a URL {}".
                          format(graphical_abstract))

            logAssert(type(arrow.get(date)) == arrow.arrow.Arrow,
                      "The date is not really a date {}".format(date))

            logAssert(topic_simple.startswith(' ') is True,
                      "Topic doesn't start with space {}".format(topic_simple))

            logAssert(topic_simple.endswith(' ') is True,
                      "Topic doesn't end with space {}".format(topic_simple))

            if author_simple is not None:
                logAssert(author_simple.startswith(' ') is True,
                          "author_simple doesn't start with space {}".
                          format(author_simple))
                logAssert(author_simple.endswith(' ') is True,
                          "author_simple doesn't end with space {}".
                          format(author_simple))

    l.debug("Time spent in test_getData: {}".
            format(datetime.datetime.now() - start_time))


def test_getDoi(journalsUrls):

    """Tests if the function getDoi gets the DOI correctly"""

    l.debug("Starting test getDoi")
    start_time = datetime.datetime.now()

    list_sites = journalsUrls

    # Build a dic with key: company
                     # value: journal name
    dict_journals = {}
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        dict_journals[company] = hosts.getJournals(company)[0]


    for site in list_sites:
        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        # Get the company name
        for publisher, data in dict_journals.items():
            if journal in data:
                company = publisher

        l.info("{}: {}".format(site, len(feed.entries)))

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests LENGTH_SAMPLE entries for a journal, not all of them
        for entry in samples:

            doi = hosts.getDoi(company, journal, entry)
            l.info(doi)

            logAssert(type(doi) == str or not doi.startswith('10.1'),
                      "DOI is not a string or is not a DOI {}".
                      format(doi))

    l.debug("Time spent in test_getDoi: {}".
            format(datetime.datetime.now() - start_time))
