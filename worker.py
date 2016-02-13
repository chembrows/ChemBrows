#!/usr/bin/python
# coding: utf-8



import os
from PyQt4 import QtSql, QtCore
import feedparser
import functools
from requests_futures.sessions import FuturesSession
import requests
import socket
import traceback
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


    def __init__(self, logger, bdd, parent):

        QtCore.QThread.__init__(self)

        self.l = logger

        self.bdd = bdd
        self.parent = parent
        self.dict_journals = parent.dict_journals

        # Define a path attribute to easily change it
        # for the tests
        self.DATA_PATH = self.parent.DATA_PATH + "/graphical_abstracts/"

        # Set the timeout for the futures
        # W/ a large timeout, less chances to get en exception
        self.TIMEOUT = 20

        self.count_futures_urls = 0
        self.count_futures_images = 0

        # Count the entries added by a particular worker
        self.new_entries_worker = 0

        # Store the futures in this list. Easier to kill them
        self.list_futures = []


    def setUrl(self, url_feed):

        self.url_feed = url_feed


    def __del__(self):

        """Method to destroy the thread properly"""

        self.wait()
        self.l.debug("Deleting thread")


    def run(self):

        """Main function. Starts the real business"""

        self.l.debug("Entering worker")
        self.l.debug(self.url_feed)

        # Get the RSS page of the url provided
        try:
            self.feed = feedparser.parse(self.url_feed)
            self.l.debug("RSS page successfully dled")
        except OSError:
            self.l.error("Too many files open, could not start the thread !")
            return

        # Get the journal name
        try:
            journal = self.feed['feed']['title']
        except KeyError:
            self.l.critical("No title for the journal ! Aborting")
            self.l.critical(self.url_feed)
            return

        self.l.info("{0}: {1}".format(journal, len(self.feed.entries)))

        # Lists to check if the post is in the db, and if
        # it has all the infos
        self.session_images = FuturesSession(max_workers=20)

        # Get the company and the journal_abb by scrolling the dictionnary
        # containing all the data regarding the journals implemented in the
        # program. This dictionnary is built in gui.py, to avoid multiple calls
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
            return

        # Create a list for the journals which a dl of the article
        # page is not required. All the data are in the rss page
        company_no_dl = ['science', 'elsevier', 'beilstein', 'plos']

        query = QtSql.QSqlQuery(self.bdd)

        self.bdd.transaction()

        # The feeds of these journals are complete
        # if journal in wiley + science + elsevier:
        if company in company_no_dl:

            self.count_futures_urls += len(self.feed.entries)

            for entry in self.feed.entries:

                # Get the DOI, a unique number for a publication
                doi = hosts.getDoi(company, journal, entry)

                # Reject crappy entries: corrigendum, erratum, etc
                if hosts.reject(entry.title):
                    title = entry.title
                    self.count_futures_images += 1
                    self.parent.counter_rejected += 1
                    self.l.debug("Rejecting {0}".format(doi))

                    # Insert the crappy articles in a rescue database
                    if self.parent.debug_mod and doi not in self.dico_doi:
                        url = getattr(entry, 'feedburner_origlink', entry.link)
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
                    self.count_futures_images += 1
                    self.l.debug("Skipping {}".format(doi))
                    continue

                # Artice not complete, try to complete it
                elif doi in self.dico_doi and not self.dico_doi[doi]:

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

                        if os.path.exists(self.DATA_PATH +
                                          functions.simpleChar(
                                              graphical_abstract)):
                            self.count_futures_images += 1
                        else:
                            url = getattr(entry, 'feedburner_origlink',
                                          entry.link)

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
                        self.count_futures_images += 1
                        continue

                else:
                    try:
                        title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry)
                    except TypeError:
                        self.l.error("getData returned None for {}".
                                     format(journal))
                        self.count_futures_images += 1
                        return

                    # Rejecting article if no author
                    if authors == "Empty":
                        self.count_futures_images += 1
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
                              graphical_abstract, url, 1, topic_simple, author_simple)

                    self.l.debug("Adding {0} to the database".format(doi))
                    self.parent.counter += 1
                    self.new_entries_worker += 1

                    for value in params:
                        query.addBindValue(value)
                    query.exec_()

                    if graphical_abstract == "Empty" or os.path.exists(
                            self.DATA_PATH +
                            functions.simpleChar(graphical_abstract)):

                        self.count_futures_images += 1

                        # This block is executed when you delete the db, but
                        # not the images. Allows to update the
                        # graphical_abstract in db accordingly
                        if os.path.exists(self.DATA_PATH +
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

        else:

            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0',
                       'Connection': 'close'}

            self.session_pages = FuturesSession(max_workers=20)

            for entry in self.feed.entries:

                doi = hosts.getDoi(company, journal, entry)

                # Reject crappy entries: corrigendum, erratum, etc
                if hosts.reject(entry.title):
                    title = entry.title
                    self.count_futures_images += 1
                    self.count_futures_urls += 1
                    self.parent.counter_rejected += 1
                    self.l.debug("Rejecting {0}".format(doi))

                    if self.parent.debug_mod and doi not in self.dico_doi:
                        url = getattr(entry, 'feedburner_origlink', entry.link)
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
                    self.count_futures_images += 1
                    self.count_futures_urls += 1
                    self.l.debug("Skipping {}".format(doi))
                    continue


                # Article not complete, try to complete it
                elif doi in self.dico_doi and not self.dico_doi[doi]:

                    url = getattr(entry, 'feedburner_origlink', entry.link)

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
                        self.count_futures_urls += 1

                        graphical_abstract = data['graphical_abstract']

                        if os.path.exists(self.DATA_PATH +
                                          functions.simpleChar(
                                              graphical_abstract)):
                            self.count_futures_images += 1
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
                        self.count_futures_urls += 1
                        self.count_futures_images += 1
                        continue

                else:

                    self.l.debug("Starting adding new entry")

                    url = getattr(entry, 'feedburner_origlink', entry.link)

                    future = self.session_pages.get(url, timeout=self.TIMEOUT,
                                                    headers=headers)
                    future.add_done_callback(functools.partial(
                        self.completeData, doi, company, journal, journal_abb,
                        entry))
                    self.list_futures.append(future)


        # Check if the counters are full
        while ((self.count_futures_images + self.count_futures_urls) !=
                len(self.feed.entries) * 2 and self.parent.parsing):
            self.sleep(1)

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
        self.count_futures_urls += 1

        if not self.parent.parsing:
            return

        try:
            response = future.result()
        except requests.exceptions.ReadTimeout:
            self.l.error("ReadTimeout for {}".format(journal))
            self.count_futures_images += 1
            return
        except requests.exceptions.ConnectionError:
            self.l.error("ConnectionError for {}".format(journal))
            self.count_futures_images += 1
            return
        except ConnectionResetError:
            self.l.error("ConnectionResetError for {}".format(journal))
            self.count_futures_images += 1
            return
        except socket.timeout:
            self.l.error("socket.timeout for {}".format(journal))
            self.count_futures_images += 1
            return
        except concurrent.futures._base.CancelledError:
            self.l.error("future cancelled for {}".format(journal))
            self.count_futures_images += 1
            return
        except Exception as e:
            self.l.error("Unknown exception {} for {}".format(e, journal))
            self.l.error(traceback.format_exc())
            self.count_futures_images += 1
            return

        query = QtSql.QSqlQuery(self.bdd)

        try:
            title, date, authors, abstract, graphical_abstract, url, topic_simple, author_simple = hosts.getData(company, journal, entry, response)
            # self.l.debug("ck 1.7")
        except TypeError:
            self.l.error("getData returned None for {}".format(journal))
            self.count_futures_images += 1
            return
        except Exception as e:
            self.l.error("Unknown exception completeData {}".format(e))
            self.l.error(traceback.format_exc())
            self.count_futures_images += 1
            return

        # Rejecting the article if no authors
        if authors == "Empty":
            self.count_futures_images += 1
            self.parent.counter_rejected += 1
            self.l.debug("Rejecting article {}, no author".format(title))
            return

        # Check if the DOI is already in the db. Mandatory, bc sometimes
        # updateData will tell the worker to dl the page before downloading
        # the picture
        if doi not in self.dico_doi:
            query.prepare("INSERT INTO papers (doi, title, date, journal, \
                          authors, abstract, graphical_abstract, url, new, \
                          topic_simple, author_simple) VALUES(?, ?, ?, ?, ?, \
                          ?, ?, ?, ?, ?, ?)")

            params = (doi, title, date, journal_abb, authors, abstract,
                      graphical_abstract, url, 1, topic_simple, author_simple)

            self.l.debug("Adding {0} to the database".format(doi))
            self.parent.counter += 1

            for value in params:
                query.addBindValue(value)

            query.exec_()

        self.new_entries_worker += 1

        # Don't try to dl the image if its url is 'Empty', or if the image
        # already exists
        if (graphical_abstract == "Empty" or
                os.path.exists(self.DATA_PATH +
                               functions.simpleChar(graphical_abstract))):
            self.count_futures_images += 1
            self.l.debug("Image already dled or Empty")

            # This block is executed when you delete the db, but not the
            # images. Allows to update the graphical_abstract in db accordingly
            if os.path.exists(self.DATA_PATH +
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
            return
        except Exception as e:
            self.l.error("Exception raised in pictureDownloaded{}".format(e))
            self.l.error(traceback.format_exc())
            params = ("Empty", doi)
        else:
            # If the picture was dled correctly
            if response.status_code is requests.codes.ok:
                try:
                    # Save the page
                    io = BytesIO(response.content)
                    Image.open(io).convert('RGB').save(
                        self.DATA_PATH + functions.simpleChar(response.url),
                        format='JPEG')
                    self.l.debug("Image ok")
                except Exception as e:
                    self.l.error("An error occured in pictureDownloaded: {}".
                                 format(e))
                    self.l.error(traceback.format_exc())
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

        self.count_futures_images += 1


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
