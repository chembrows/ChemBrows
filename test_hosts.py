#!/usr/bin/python
# -*-coding:Utf-8 -*

import os
import feedparser
import requests
import pytest
import random

import hosts


# worker = Worker(site, self.l, self.bdd)

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

    assert type(rsc) == tuple
    assert type(acs) == tuple
    assert type(wiley) == tuple
    assert type(npg) == tuple
    assert type(science) == tuple
    assert type(nas) == tuple
    assert type(elsevier) == tuple

    total = rsc + acs + wiley + npg + science + nas + elsevier

    for publisher in total:
        for chain in publisher:
            assert type(chain) == str

@pytest.fixture()
def journalsUrls():

    """Returns a list. One journal per publisher,
    chosen randomly from all the journals of each publisher"""

    urls = []
    _, rsc_abb, rsc_urls = hosts.getJournals("rsc")
    _, acs_abb, acs_urls = hosts.getJournals("acs")
    _, wiley_abb, wiley_urls = hosts.getJournals("wiley")
    _, npg_abb, npg_urls = hosts.getJournals("npg")
    _, science_abb, science_urls = hosts.getJournals("science")
    _, nas_abb, nas_urls = hosts.getJournals("nas")
    _, elsevier_abb, elsevier_urls = hosts.getJournals("elsevier")

    # Pick one site from each publisher
    urls.append(random.choice(rsc_urls))
    urls.append(random.choice(acs_urls))
    urls.append(random.choice(wiley_urls))
    urls.append(random.choice(npg_urls))
    urls.append(random.choice(science_urls))
    urls.append(random.choice(nas_urls))
    urls.append(random.choice(elsevier_urls))

    abbs = rsc_abb + acs_abb + wiley_abb + npg_abb + science_abb + nas_abb + elsevier_abb
    sites_urls = rsc_urls + acs_urls + wiley_urls + npg_urls + science_urls + nas_urls + elsevier_urls

    print("\n")
    for site in urls:
        print(abbs[sites_urls.index(site)])

    return urls


def test_getData(journalsUrls):

    print("\n")
    print("Starting test getData")

    list_sites = journalsUrls

    rsc = hosts.getJournals("rsc")[0]
    acs = hosts.getJournals("acs")[0]
    wiley = hosts.getJournals("wiley")[0]
    npg = hosts.getJournals("npg")[0]
    science = hosts.getJournals("science")[0]
    nas = hosts.getJournals("nas")[0]
    elsevier = hosts.getJournals("elsevier")[0]

    i = 1
    for site in list_sites:
        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        # Tests 3 entries for a journal, not all of them
        for entry in random.sample(feed.entries, 3):

            if journal in science + wiley:
                title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry)
            else:
                try:
                    url = entry.feedburner_origlink
                except AttributeError:
                    url = entry.link

                response = requests.get(url, timeout=10)
                title, journal_abb, date, authors, abstract, graphical_abstract, url, topic_simple = hosts.getData(journal, entry, response)

            print("Sample {} of {}".format(i, 21))
            print(title)
            print(url)
            print(graphical_abstract)
            print("\n")

            assert type(abstract) == str
            assert type(url) == str
            assert type(graphical_abstract) == str

            i += 1


def test_getDoi(journalsUrls):

    print("\n")
    print("Starting test getDoi")

    list_sites = journalsUrls

    for site in list_sites:
        feed = feedparser.parse(site)
        journal = feed['feed']['title']

        print("{}: {}".format(site, len(feed.entries)))

        # Tests 3 entries for a journal, not all of them
        for entry in random.sample(feed.entries, 3):

            doi = hosts.getDoi(journal, entry)
            print(doi)

            assert type(doi) == str
