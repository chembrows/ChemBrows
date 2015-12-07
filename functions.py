#!/usr/bin/python
# coding: utf-8


import sys
import os
import arrow
import re


def unidecodePerso(string):

    if getattr(sys, "frozen", False):
        resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        resource_dir = '.'

    with open(os.path.join(resource_dir, 'config/data.bin'), 'rb') as f:
        _replaces = f.read().decode('utf8').split('\x00')

    chars = []
    for ch in string:
        codepoint = ord(ch)

        if not codepoint:
            chars.append('\x00')
            continue

        try:
            chars.append(_replaces[codepoint - 1])
        except IndexError:
            pass
    return "".join(chars)


def prettyDate(date):

    """Prettify a date. Ex: 3 days ago"""

    now = arrow.now()
    date = arrow.get(date)

    if now.timestamp - date.timestamp < 86400:
        return "Today"
    else:
        return date.humanize(now.naive)


def simpleChar(string):

    """Sluggify the string"""
    # http://www.siteduzero.com/forum-83-810635-p1-sqlite-recherche-avec-like-insensible-a-la-casse.html#r7767300

    # http://stackoverflow.com/questions/5574042/string-slugification-in-python
    string = unidecodePerso(string).lower()

    return re.sub(r'\W+', ' ', string)


def queryString(word):

    """
    Function to return a string formatted to be
    included in a LIKE query
    Ex:
    querySting("sper*m") -> % sper%mine %
    querySting("*sperm*") -> %sperm%
    querySting("spermine") -> % spermine %
    """

    word = str(word)

    if word[0] != '*' and word[-1] != '*' and '*' in word:
        word = word.replace('*', '%')

    res = word.replace('*', '')

    if word[0] == '*':
        res = '%' + res
    else:
        res = '% ' + res

    if word[-1] == '*':
        res = res + '%'
    else:
        res = res + ' %'

    return res


def buildSearch(topic_entries, author_entries):

    """Build the query"""

    base = "SELECT * FROM papers WHERE "

    first = True

    # TOPIC, AND condition
    if topic_entries[0]:
        first = False

        # words = [word.lstrip().rstrip() for word in topic_entries[0].split(",")]
        words = [word.strip() for word in topic_entries[0].split(",")]
        words = [queryString(word) for word in words]

        for word in words:
            if word == words[0]:
                base += "topic_simple LIKE '{0}'".format(word)
            else:
                base += " AND topic_simple LIKE '{0}'".format(word)

    # TOPIC, OR condition
    if topic_entries[1]:
        # words = [word.lstrip().rstrip() for word in topic_entries[1].split(",")]
        words = [word.strip() for word in topic_entries[1].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            base += "topic_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                base += " OR topic_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                base += " OR topic_simple LIKE '{0}'".format(word)

    # TOPIC, NOT condition
    if topic_entries[2]:
        # words = [word.lstrip().rstrip() for word in topic_entries[2].split(",")]
        words = [word.strip() for word in topic_entries[2].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            base += "topic_simple NOT LIKE '{0}'".format(words[0])

            for word in words[1:]:
                base += " AND topic_simple NOT LIKE '{0}'".format(word)
        else:
            for word in words:
                base += " AND topic_simple NOT LIKE '{0}'".format(word)

    # AUTHOR, AND condition
    if author_entries[0]:
        # words = [word.lstrip().rstrip() for word in author_entries[0].split(",")]
        words = [word.strip() for word in author_entries[0].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(words[0])
            base += "' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(words[0])
            # base += "authors_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " AND authors_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " AND authors_simple LIKE '{0}'".format(word)

    # AUTHOR, OR condition
    if author_entries[1]:
        # words = [word.lstrip().rstrip() for word in author_entries[1].split(",")]
        words = [word.strip() for word in author_entries[1].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(words[0])
            base += "' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(words[0])
            # base += "authors_simple LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " OR ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " OR ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " OR authors_simple LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " OR ', ' || replace(authors, ',', ' ,') || ' ,' LIKE ',{0},'".format(word)
                base += " OR ' ' || replace(authors, ',', ' ') || ' ' LIKE '{0}'".format(word)
                # base += " OR authors_simple LIKE '{0}'".format(word)

    # AUTHOR, NOT condition
    if author_entries[2]:
        # words = [word.lstrip().rstrip() for word in author_entries[2].split(",")]
        words = [word.strip() for word in author_entries[2].split(",")]
        words = [queryString(word) for word in words]

        if first:
            first = False
            # base += "', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(words[0])
            base += "', ' || replace(authors, ',', ' ') || ' ,' NOT LIKE '{0}'".format(words[0])
            # base += "authors_simple NOT LIKE '{0}'".format(words[0])

            for word in words[1:]:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{0}'".format(word)
                # base += " AND authors_simple NOT LIKE '{0}'".format(word)
        else:
            for word in words:
                # base += " AND ', ' || replace(authors, ',', ' ,') || ' ,' NOT LIKE ',{0},'".format(word)
                base += " AND ' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{0}'".format(word)
                # base += " AND authors_simple NOT LIKE '{0}'".format(word)

    return base


def removeHtml(data):

    """Simple function to remove html tags.
    Not very robust, but does the job.
    Used in gui.shareByEmail"""

    p = re.compile(r'<.*?>')

    return p.sub('', data)



if __name__ == "__main__":
    # like(10)
    # _, dois = listDoi()
    # print(dois)
    # queryString("sper**mine")
    # queryString("*sperm*")
    # queryString("spermine")
    # checkData()

    # match(['jean-patrick francoia', 'robert pascal', 'laurent vial'], "r* pascal")

    # unidecodePerso('test')
    pass
