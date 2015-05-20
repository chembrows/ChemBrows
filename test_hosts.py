#!/usr/bin/python
# -*-coding:Utf-8 -*

import os
import feedparser
import requests
import pytest
import random

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

    """Returns a list. All the journals of a publisher"""

    _, rsc_abb, rsc_urls = hosts.getJournals("rsc")
    _, acs_abb, acs_urls = hosts.getJournals("acs")
    _, wiley_abb, wiley_urls = hosts.getJournals("wiley")
    _, npg_abb, npg_urls = hosts.getJournals("npg")
    _, science_abb, science_urls = hosts.getJournals("science")
    _, nas_abb, nas_urls = hosts.getJournals("nas")
    _, elsevier_abb, elsevier_urls = hosts.getJournals("elsevier")
    _, thieme_abb, thieme_urls = hosts.getJournals("thieme")
    _, beil_abb, beil_urls = hosts.getJournals("beilstein")

    urls = rsc_urls + acs_urls + wiley_urls + npg_urls + science_urls + \
           nas_urls + elsevier_urls + thieme_urls + beil_urls

    return urls


def test_getData(journalsUrls):

    print("\n")
    print("Starting test getData")

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
