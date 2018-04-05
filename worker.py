#!/usr/bin/python
# coding: utf-8

import os
from PyQt5 import QtSql, QtCore
import feedparser
import functools
from requests_futures.sessions import FuturesSession
import requests
import socket
import concurrent

from io import BytesIO
from PIL import Image
# from io import open as iopen

# DEBUG
# from memory_profiler import profile
# import sys

# Personal
import hosts
import functions


class Worker(QtCore.QThread):

    """Subclassing the class in order to provide a thread.
    The thread is used to parse the RSS flux, in background. The
    main UI remains functional"""

    # http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
    # https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots


    def __init__(self, parent):

        QtCore.QThread.__init__(self)

        self.l = parent.l

        self.bdd = parent.bdd
        self.parent = parent
        self.dict_journals = parent.dict_journals

        self.url_feed = ""

        # Define a path attribute to easily change it
        # for the tests
        self.PATH = self.parent.DATA_PATH + "/graphical_abstracts/"

        # Set the timeout for the futures
        # W/ a large timeout, less chances to get en exception
        self.TIMEOUT = 20

        # Maximum nbr of concurrent workers. Set for session_images and
        # session_pages
        self.MAX_WORKERS = 20

        self.counter_futures_urls = 0
        self.counter_futures_images = 0

        # Count the entries added by a particular worker
        self.new_entries_worker = 0

        # Store the futures in this list. Easier to kill them
        self.list_futures = []


    def _getFeed(self, timeout: int) -> feedparser.util.FeedParserDict:

        self.l.debug(self.url_feed)

        try:
            # Get the RSS page of the url provided
            feed = feedparser.parse(self.url_feed, timeout=timeout)

            # Check if the feed has a title (journal's name)
            journal = feed['feed']['title']

            self.l.debug("RSS page successfully dled")
            return feed

        except Exception as e:
            self.l.error("RSS page {} could not be downloaded: {}. Handled".
                         format(self.url_feed, e), exc_info=True)
            return None


    def run(self):

        """Main function. Starts the real business"""

        self.l.debug("Entering worker")

        feed = self._getFeed(timeout=self.TIMEOUT)

        if feed is None:
            self.l.error("Exiting worker, problem w/ the feed")
            self.parent.list_failed_rss.append(self.url_feed)
            return

        # Get the journal name
        journal = feed['feed']['title']

        self.l.info("{}: {}".format(journal, len(feed.entries)))

        # Lists to check if the post is in the db, and if
        # it has all the info
        self.session_images = FuturesSession(max_workers=self.MAX_WORKERS,
            session=self.parent.browsing_session)

        # Get the company and the journal_abb by scrolling the dictionary
        # containing all the data regarding the journals implemented in the
        # program. This dictionary is built in gui.py, to avoid multiple calls
        # to hosts.getJournals
        # care_image determines if the Worker will try to dl the graphical
        # abstracts
        for key, tuple_data in self.dict_journals.items():
            if journal in tuple_data[0]:
                company = key
                index = tuple_data[0].index(journal)
                journal_abb = tuple_data[1][index]
                care_image = tuple_data[3][index]
                break

        try:
            self.dico_doi = self.listDoi(journal_abb)
        except UnboundLocalError:
            self.l.error("Journal not recognized ! Aborting")
            self.parent.list_failed_rss.append(self.url_feed)
            return

        # Create a list for the journals which a dl of the article
        # page is not required. All the data are in the rss page
        company_no_dl = ['Science', 'Elsevier', 'Beilstein', 'PLOS',
                         'ChemArxiv', 'Wiley']

        query = QtSql.QSqlQuery(self.bdd)

        self.bdd.transaction()

        # The feeds of these journals are complete
        if company in company_no_dl:

            self.counter_futures_urls += len(feed.entries)

            for entry in feed.entries:

                # Get the DOI, a unique number for a publication
                try:
                    doi = hosts.getDoi(company, journal, entry)
                except Exception as e:
                    self.l.error("getDoi failed for: {}".
                                 format(journal), exc_info=True)
                    self.counter_futures_urls += 1
                    continue

                try:
                    url = hosts.refineUrl(company, journal, entry)
                except Exception as e:
                    self.l.error("refineUrl failed for: {}".
                                 format(journal), exc_info=True)
                    self.counter_futures_urls += 1
                    continue

                # Reject crappy entries: corrigendum, erratum, etc
                if hosts.reject(entry.title):
                    title = entry.title
                    self.counter_futures_images += 1
                    self.parent.counter_rejected += 1
                    self.l.debug("Rejecting {0}".format(doi))

                    # Insert the crappy articles in a rescue database
                    if self.parent.debug_mod and doi not in self.dico_doi:
                        query.prepare("INSERT INTO debug (doi, title, \
                                      journal, url) VALUES(?, ?, ?, ?)")
                        params = (doi, title, journal_abb, url)
                        self.l.debug("Inserting {0} in table debug".
                                     format(doi))
                        for value in params:
                            query.addBindValue(value)
                        query.exec_()
                    else:
                        continue

                # Artice complete, skip it
                elif doi in self.dico_doi and self.dico_doi[doi]:
                    self.counter_futures_images += 1
                    self.l.debug("Skipping {}".format(doi))
                    continue

                # Artice not complete, try to complete it
                elif doi in self.dico_doi and not self.dico_doi[doi]:
                    self.l.debug("Trying to update {}".format(doi))

                    # How to update the entry
                    dl_page, dl_image, data = hosts.updateData(company,
                                                               journal,
                                                               entry,
                                                               care_image)

                    # For these journals, all the infos are in the RSS.
                    # Only care about the image
                    if dl_image:
                        self.parent.counter_updates += 1

                        graphical_abstract = data['graphical_abstract']

                        if os.path.exists(self.PATH +
                                          functions.simpleChar(
                                              graphical_abstract)):
                            self.counter_futures_images += 1
                        else:
                            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                                       'Connection': 'close',
                                       'Referer': url}

                            future_image = self.session_images.get(
                                graphical_abstract, headers=headers,
                                timeout=self.TIMEOUT)
                            future_image.add_done_callback(functools.partial(
                                self.pictureDownloaded, doi, url))
                            self.list_futures.append(future_image)

                    else:
                        self.counter_futures_images += 1
                        continue

                # New article, treat it
                else:
                    try:
                        title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry)
                    except Exception as e:
                        self.l.error("Problem with getData: {}".
                                     format(journal), exc_info=True)
                        self.counter_futures_images += 1
                        self.parent.counter_articles_failed += 1
                        return

                    # Rejecting article if no author
                    if authors == "Empty":
                        self.counter_futures_images += 1
                        self.parent.counter_rejected += 1
                        self.l.debug("Rejecting article {}, no author".
                                     format(title))
                        continue

                    query.prepare("INSERT INTO papers (doi, title, date, \
                                  journal, authors, abstract, \
                                  graphical_abstract, url, new, topic_simple, \
                                  author_simple) \
                                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

                    # Set new to 1 and not to true
                    params = (doi, title, date, journal_abb, authors, abstract,
                              graphical_abstract, url, 1, topic_simple,
                              author_simple)

                    for value in params:
                        query.addBindValue(value)

                    # Test that query worked
                    if not query.exec_():
                        self.l.error("SQL ERROR in run(): {}, company_no_dl".
                                     format(query.lastError().text()))
                        self.parent.counter_articles_failed += 1
                        continue
                    else:
                        self.l.debug("{} added to the database".format(doi))
                        self.new_entries_worker += 1
                        self.parent.counter_added += 1

                    # If article has no graphical abstract of if it has been
                    # dled
                    if graphical_abstract == "Empty" or os.path.exists(
                            self.PATH +
                            functions.simpleChar(graphical_abstract)):

                        self.counter_futures_images += 1

                        # This block is executed when you delete the db, but
                        # not the images. Allows to update the
                        # graphical_abstract in db accordingly
                        if os.path.exists(self.PATH +
                                          functions.simpleChar(
                                              graphical_abstract)):

                            query.prepare("UPDATE papers SET \
                                          graphical_abstract=? WHERE doi=?")

                            params = (functions.simpleChar(graphical_abstract),
                                      doi)

                            for value in params:
                                query.addBindValue(value)
                            query.exec_()
                    else:
                        headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                                   'Connection': 'close',
                                   'Referer': url}

                        future_image = self.session_images.get(
                            graphical_abstract, headers=headers,
                            timeout=self.TIMEOUT)

                        future_image.add_done_callback(
                            functools.partial(self.pictureDownloaded,
                                              doi, url))

                        self.list_futures.append(future_image)

        # The company requires to download the article's web page
        else:

            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                       'Connection': 'close'}

            self.session_pages = FuturesSession(max_workers=self.MAX_WORKERS,
                session=self.parent.browsing_session)

            for entry in feed.entries:

                # Get the DOI, a unique number for a publication
                try:
                    doi = hosts.getDoi(company, journal, entry)
                except Exception as e:
                    self.l.error("getDoi failed for: {}".
                                 format(journal), exc_info=True)
                    self.counter_futures_urls += 1
                    self.counter_futures_images += 1
                    continue

                # Try to refine the url
                try:
                    url = hosts.refineUrl(company, journal, entry)
                except Exception as e:
                    self.l.error("refineUrl failed for: {}".
                                 format(journal), exc_info=True)
                    self.counter_futures_urls += 1
                    self.counter_futures_images += 1
                    continue

                # Make sure the entry has a title
                try:
                    title = entry.title
                except AttributeError:
                    self.l.error("No title for {}".
                                 format(doi), exc_info=True)
                    self.counter_futures_urls += 1
                    self.counter_futures_images += 1
                    continue

                # Reject crappy entries: corrigendum, erratum, etc
                if hosts.reject(title):
                    self.counter_futures_images += 1
                    self.counter_futures_urls += 1
                    self.parent.counter_rejected += 1
                    self.l.debug("Rejecting {0}".format(doi))

                    if self.parent.debug_mod and doi not in self.dico_doi:
                        query.prepare("INSERT INTO debug (doi, title, \
                                      journal, url) VALUES(?, ?, ?, ?)")
                        params = (doi, title, journal_abb, url)

                        for value in params:
                            query.addBindValue(value)
                        query.exec_()

                        self.l.debug("Inserting {0} in table debug".
                                     format(doi))
                    continue


                # Article complete, skip it
                elif doi in self.dico_doi and self.dico_doi[doi]:
                    self.counter_futures_images += 1
                    self.counter_futures_urls += 1
                    self.l.debug("Skipping {}".format(doi))
                    continue


                # Article not complete, try to complete it
                elif doi in self.dico_doi and not self.dico_doi[doi]:

                    url = hosts.refineUrl(company, journal, entry)

                    dl_page, dl_image, data = hosts.updateData(company,
                                                               journal,
                                                               entry,
                                                               care_image)

                    if dl_page:
                        self.parent.counter_updates += 1

                        future = self.session_pages.get(url,
                                                        timeout=self.TIMEOUT,
                                                        headers=headers)
                        future.add_done_callback(functools.partial(
                            self.completeData, doi, company, journal,
                            journal_abb, entry))
                        self.list_futures.append(future)

                        # Continue just to be sure. If dl_page is True,
                        # dl_image is likely True too
                        continue

                    elif dl_image:
                        self.parent.counter_updates += 1
                        self.counter_futures_urls += 1

                        graphical_abstract = data['graphical_abstract']

                        if os.path.exists(self.PATH +
                                          functions.simpleChar(
                                              graphical_abstract)):
                            self.counter_futures_images += 1
                        else:
                            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                                       'Connection': 'close',
                                       'Referer': url}

                            future_image = self.session_images.get(
                                graphical_abstract, headers=headers,
                                timeout=self.TIMEOUT)
                            future_image.add_done_callback(functools.partial(
                                self.pictureDownloaded, doi, url))
                            self.list_futures.append(future_image)

                    else:
                        self.counter_futures_urls += 1
                        self.counter_futures_images += 1
                        continue

                # New article, treat it
                else:

                    url = hosts.refineUrl(company, journal, entry)
                    self.l.debug("Starting adding new entry")

                    future = self.session_pages.get(url, timeout=self.TIMEOUT,
                                                    headers=headers)
                    future.add_done_callback(functools.partial(
                        self.completeData, doi, company, journal, journal_abb,
                        entry))
                    self.list_futures.append(future)


        # Check if the counters are full
        while ((self.counter_futures_images + self.counter_futures_urls) !=
                len(feed.entries) * 2 and self.parent.parsing):
            self.sleep(0.5)

        if self.parent.parsing:
            if not self.bdd.commit():
                self.l.error(self.bdd.lastError().text())
                self.l.debug("db insertions/modifications: {}".
                             format(self.new_entries_worker))
                self.l.error("Problem when comitting data for {}".
                             format(journal))

        # Free the memory, and clean the remaining futures
        try:
            self.session_pages.executor.shutdown()
        except AttributeError:
            self.l.error("No session_pages to shut down")

        self.session_images.executor.shutdown()
        self.l.debug("Exiting thread for {}".format(journal))


    def completeData(self, doi, company, journal, journal_abb, entry, future):

        """Callback to handle the response of the futures trying to
        download the page of the articles"""

        self.l.debug("Page dled")
        self.counter_futures_urls += 1

        if not self.parent.parsing:
            return

        try:
            response = future.result()
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError, ConnectionResetError,
                socket.timeout, concurrent.futures._base.CancelledError) as e:

            self.l.error("{} raised for {}. Handled".format(journal, e))
            self.counter_futures_images += 1
            self.parent.counter_articles_failed += 1
            return
        except Exception as e:
            self.l.error("Unknown exception {} for {}".format(e, journal),
                         exc_info=True)
            self.counter_futures_images += 1
            self.parent.counter_articles_failed += 1
            return

        query = QtSql.QSqlQuery(self.bdd)

        try:
            title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry, response)
        except TypeError:
            self.l.error("getData returned None for {}".format(journal),
                         exc_info=True)
            self.counter_futures_images += 1
            self.parent.counter_articles_failed += 1
            return
        except Exception as e:
            self.l.error("Unknown exception completeData {}".format(e),
                         exc_info=True)
            self.counter_futures_images += 1
            self.parent.counter_articles_failed += 1
            return

        # Rejecting the article if no authors
        if authors == "Empty":
            self.counter_futures_images += 1
            self.parent.counter_rejected += 1
            self.l.debug("Rejecting article {}, no author".format(title))
            return

        # Check if the DOI is already in the db. Mandatory, bc sometimes
        # updateData will tell the worker to dl the page before downloading
        # the picture
        if doi not in self.dico_doi:
            query.prepare("INSERT INTO papers (doi, title, date, journal, \
                          authors, abstract, graphical_abstract, url, new, \
                          topic_simple, author_simple) VALUES(?, \
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            params = (doi, title, date, journal_abb, authors, abstract,
                      graphical_abstract, url, 1, topic_simple, author_simple)

            self.l.debug("Adding {} to the database".format(doi))
            self.parent.counter_added += 1

            for value in params:
                query.addBindValue(value)

            # Test that query worked
            if not query.exec_():
                self.l.error("SQL ERROR in completeData(): {}".
                             format(query.lastError().text()))
                self.parent.counter_articles_failed += 1
                return
            else:
                self.new_entries_worker += 1

        # Don't try to dl the image if its url is 'Empty', or if the image
        # already exists
        if (graphical_abstract == "Empty" or
                os.path.exists(self.PATH +
                               functions.simpleChar(graphical_abstract))):
            self.counter_futures_images += 1
            self.l.debug("Image already dled or Empty")

            # This block is executed when you delete the db, but not the
            # images. Allows to update the graphical_abstract in db accordingly
            if os.path.exists(self.PATH +
                              functions.simpleChar(graphical_abstract)):
                query.prepare("UPDATE papers SET graphical_abstract=? WHERE \
                              doi=?")
                params = (functions.simpleChar(graphical_abstract), doi)
                for value in params:
                    query.addBindValue(value)
                query.exec_()
        else:
            self.l.debug("Page dled, adding future image")
            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                       'Connection': 'close',
                       'Referer': url}

            future_image = self.session_images.get(graphical_abstract,
                                                   headers=headers,
                                                   timeout=self.TIMEOUT)
            future_image.add_done_callback(functools.partial(
                self.pictureDownloaded, doi, url))
            self.list_futures.append(future_image)


    def pictureDownloaded(self, doi, entry_url, future):

        """Callback to handle the response of the futures
        downloading a picture"""

        if not self.parent.parsing:
            return

        query = QtSql.QSqlQuery(self.bdd)

        try:
            response = future.result()
        except concurrent.futures._base.CancelledError:
            self.l.error("future cancelled for {}".format(entry_url))
            self.parent.counter_images_failed += 1
            params = ("Empty", doi)
        except Exception as e:
            self.parent.counter_images_failed += 1
            self.l.error("pictureDownloaded: {}".format(e), exc_info=True)
            params = ("Empty", doi)
        else:
            # If the picture was dled correctly
            if response.status_code is requests.codes.ok:
                try:
                    # Save the page
                    io = BytesIO(response.content)
                    Image.open(io).convert('RGB').save(
                        self.PATH + functions.simpleChar(response.url),
                        format='JPEG')
                    self.l.debug("Image ok")
                except Exception as e:
                    self.l.error("An error occured in pictureDownloaded:\n{}".
                                 format(e), exc_info=True)
                    params = ("Empty", doi)
                else:
                    params = (functions.simpleChar(response.url), doi)
            else:
                self.l.debug("Bad return code: {} DOI: {}".
                             format(response.status_code, doi))
                params = ("Empty", doi)

        finally:
            query.prepare("UPDATE papers SET graphical_abstract=? WHERE doi=?")

            for value in params:
                query.addBindValue(value)

            self.new_entries_worker += 1
            query.exec_()

        self.counter_futures_images += 1


    def listDoi(self, journal_abb):

        """Function to get the doi from the database.
        Also returns a list of booleans to check if the data are complete"""

        query = QtSql.QSqlQuery(self.bdd)
        query.prepare("SELECT * FROM papers WHERE journal=?")
        query.addBindValue(journal_abb)
        query.exec_()

        result = dict()

        while query.next():
            record = query.record()
            doi = record.value('doi')

            not_empty = record.value('graphical_abstract') != "Empty"
            result[doi] = not_empty

        if self.parent.debug_mod:
            query.prepare("SELECT doi FROM debug WHERE journal=?")
            query.addBindValue(journal_abb)
            query.exec_()
            while query.next():
                result[query.record().value('doi')] = None

        return result
