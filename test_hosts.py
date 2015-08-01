#!/usr/bin/python
# -*-coding:Utf-8 -*

import os
import feedparser
import requests
import pytest
import random
import datetime
from bs4 import BeautifulSoup

import hosts

LENGTH_SAMPLE = 5


def test_getJournals():

    print("\n")
    print("Starting test getJournals")

    rsc = hosts.getJournals("rsc")
    acs = hosts.getJournals("acs")
    wiley = hosts.getJournals("wiley")
    npg = hosts.getJournals("npg")
    science = hosts.getJournals("science")
    nas = hosts.getJournals("nas")
    elsevier = hosts.getJournals("elsevier")
    thieme = hosts.getJournals("thieme")
    beil = hosts.getJournals("beilstein")

    assert type(rsc) == tuple
    assert type(acs) == tuple
    assert type(wiley) == tuple
    assert type(npg) == tuple
    assert type(science) == tuple
    assert type(nas) == tuple
    assert type(elsevier) == tuple
    assert type(thieme) == tuple
    assert type(beil) == tuple

    total = rsc + acs + wiley + npg + science + nas + elsevier + thieme + beil

    for publisher in total:
        for chain in publisher:
            assert type(chain) == str


@pytest.fixture()
def journalsUrls():

    """Returns a combined list. All the journals of all the companies"""

    rsc_urls = hosts.getJournals("rsc")[2]
    acs_urls = hosts.getJournals("acs")[2]
    wiley_urls = hosts.getJournals("wiley")[2]
    npg_urls = hosts.getJournals("npg")[2]
    science_urls = hosts.getJournals("science")[2]
    nas_urls = hosts.getJournals("nas")[2]
    elsevier_urls = hosts.getJournals("elsevier")[2]
    thieme_urls = hosts.getJournals("thieme")[2]
    beil_urls = hosts.getJournals("beilstein")[2]

    urls = rsc_urls + acs_urls + wiley_urls + npg_urls + science_urls + \
           nas_urls + elsevier_urls + thieme_urls + beil_urls

    return urls


def test_getData(journalsUrls):

    """Tests the function getData. For each journal of each company,
    tests LENGTH_SAMPLE entries"""

    print("\n")
    print("Starting test getData")

    # Returns a list of the urls of the feed pages
    list_sites = journalsUrls

    # Get the names of the journals, per company
    rsc = hosts.getJournals("rsc")[0]
    acs = hosts.getJournals("acs")[0]
    wiley = hosts.getJournals("wiley")[0]
    npg = hosts.getJournals("npg")[0]
    science = hosts.getJournals("science")[0]
    nas = hosts.getJournals("nas")[0]
    elsevier = hosts.getJournals("elsevier")[0]
    thieme = hosts.getJournals("thieme")[0]
    beil = hosts.getJournals("beilstein")[0]

    # All the journals are tested
    for site in list_sites:

        print("Site {} of {}".format(list_sites.index(site) + 1, len(list_sites)))

        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        if journal in rsc:
            company = 'rsc'
        elif journal in acs:
            company = 'acs'
        elif journal in wiley:
            company = 'wiley'
        elif journal in npg:
            company = 'npg'
        elif journal in science:
            company = 'science'
        elif journal in nas:
            company = 'nas'
        elif journal in elsevier:
            company = 'elsevier'
        elif journal in thieme:
            company = 'thieme'
        elif journal in beil:
            company = 'beilstein'

        print("\n")
        print(journal)

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests LENGTH_SAMPLE entries for a journal, not all of them
        for entry in samples:

            if journal in science + elsevier + beil:
                title, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(company, journal, entry)
            else:
                try:
                    url = entry.feedburner_origlink
                except AttributeError:
                    url = entry.link

                response = requests.get(url, timeout=10)
                title, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(company, journal, entry, response)

            print(title)
            print(url)
            print(graphical_abstract)
            print("\n")

            assert type(abstract) == str
            assert type(url) == str
            assert type(graphical_abstract) == str


def test_getDoi(journalsUrls):

    """Tests if the function getDoi gets the DOI correctly"""

    print("\n")
    print("Starting test getDoi")

    rsc = hosts.getJournals("rsc")[0]
    acs = hosts.getJournals("acs")[0]
    wiley = hosts.getJournals("wiley")[0]
    npg = hosts.getJournals("npg")[0]
    science = hosts.getJournals("science")[0]
    nas = hosts.getJournals("nas")[0]
    elsevier = hosts.getJournals("elsevier")[0]
    thieme = hosts.getJournals("thieme")[0]
    beil = hosts.getJournals("beilstein")[0]

    list_sites = journalsUrls

    for site in list_sites:
        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        if journal in rsc:
            company = 'rsc'
        elif journal in acs:
            company = 'acs'
        elif journal in wiley:
            company = 'wiley'
        elif journal in npg:
            company = 'npg'
        elif journal in science:
            company = 'science'
        elif journal in nas:
            company = 'nas'
        elif journal in elsevier:
            company = 'elsevier'
        elif journal in thieme:
            company = 'thieme'
        elif journal in beil:
            company = 'beilstein'

        print("{}: {}".format(site, len(feed.entries)))

        if len(feed.entries) < LENGTH_SAMPLE:
            samples = feed.entries
        else:
            samples = random.sample(feed.entries, LENGTH_SAMPLE)

        # Tests 3 entries for a journal, not all of them
        # for entry in random.sample(feed.entries, 3):
        for entry in samples:

            doi = hosts.getDoi(company, journal, entry)
            print(doi)

            assert type(doi) == str


def test_dlRssPages(journalsUrls):

    print("\n")
    print("Starting test dlRssPages")

    # Returns a list of the urls of the feed pages
    list_sites = journalsUrls

    headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
               'Connection': 'close'}

    print(list_sites)

    for url_feed in list_sites:

        print("Site {} of {}".format(list_sites.index(url_feed) + 1, len(list_sites)))
        feed = feedparser.parse(url_feed)

        try:
            journal = feed['feed']['title']
        except KeyError:
            print("Abort for {}".format(url_feed))

        # Get the RSS page and store it. I'll run some comparisons on them
        content = requests.get(url_feed, timeout=120, headers=headers)
        if content.status_code is requests.codes.ok:
            soup = BeautifulSoup(content.text)

            filename = "./debug_journals/" + str(journal) + "/" + str(datetime.datetime.today().date())
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w') as file:
                for line in soup.prettify():
                    file.write(line)
        else:
            print("Dl of {} not OK: {}".format(journal, content.status_code))
