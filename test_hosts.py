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

import hosts

LENGTH_SAMPLE = 3


def test_getJournals():

    """Function to get the informations about all the journals of
    a company. Returns the names, the URLs, the abbreviations, and also
    a boolean to set the download of the graphical abstracts"""

    print("\n")
    print("Starting test getJournals")

    # Create a dictionnary w/ all the data concerning the journals
    # implemented in the program: names, abbreviations, urls
    dict_journals = {}
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        dict_journals[company] = hosts.getJournals(company)

    print(dict_journals)

    for company, data in dict_journals.items():

        # data is a tuple: (list_journals_publisher,
                          # list_abb_journals_publisher,
                          # list_urls_publisher,
                          # list_bool
                         # )

        assert type(data) == tuple

        # Check that all the fields in the tuple are
        # non empty lists
        for list_info_journals in data[:-1]:
            assert type(list_info_journals) == list and list_info_journals

            # Check that all the elements in the list are
            # non empty strings
            for element in list_info_journals:
                assert type(element) == str and element

        # Check the urls of the RSS pages
        for element in data[2]:
            assert validators.url(element)

        # Check the list of booleans
        for element in data[3]:
            assert type(element) == bool


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

    print("\n")
    print("Starting test getData")

    # Returns a list of the urls of the feed pages
    list_urls_feed = journalsUrls

    # # Bypass all companies but one
    # list_urls_feed = hosts.getJournals("plos")[2]

    # Build a dic with key: company
                     # value: journal name
    dict_journals = {}
    for company in os.listdir('journals'):
        company = company.split('.')[0]
        dict_journals[company] = hosts.getJournals(company)[0]

    # All the journals are tested
    for site in list_urls_feed:

        print("Site {} of {}".format(list_urls_feed.index(site) + 1,
                                     len(list_urls_feed)))

        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        # Get the company name
        for publisher, data in dict_journals.items():
            if journal in data:
                company = publisher

        print("\n")
        print(journal)

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests LENGTH_SAMPLE entries for a journal, not all of them
        for entry in samples:

            if company in ['science', 'elsevier', 'beilstein']:
                title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry)
            else:
                url = getattr(entry, 'feedburner_origlink', entry.link)

                try:
                    response = requests.get(url, timeout=10)
                    title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry, response)
                except requests.exceptions.ReadTimeout:
                    print("A ReadTimeout occured, continue to next entry")

            print(title)
            print(url)
            print(graphical_abstract)
            print(date)
            print("\n")

            assert type(abstract) == str and abstract

            assert type(url) == str and url
            if url != 'Empty':
                # Test if url is valid
                assert validators.url(url) is True

            assert type(graphical_abstract) == str and graphical_abstract
            if graphical_abstract != 'Empty':
                assert validators.url(graphical_abstract) is True

            assert type(arrow.get(date)) == arrow.arrow.Arrow

            assert topic_simple.startswith(' ') is True
            assert topic_simple.endswith(' ') is True

            if author_simple is not None:
                assert author_simple.startswith(' ') is True
                assert author_simple.endswith(' ') is True


def test_getDoi(journalsUrls):

    """Tests if the function getDoi gets the DOI correctly"""

    print("\n")
    print("Starting test getDoi")

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

        print("{}: {}".format(site, len(feed.entries)))

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests LENGTH_SAMPLE entries for a journal, not all of them
        for entry in samples:

            doi = hosts.getDoi(company, journal, entry)
            print(doi)

            assert type(doi) == str
