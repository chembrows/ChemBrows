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


def buildSearch(topic_entries, author_entries, radio_states):

    """Build the query"""

    base = "SELECT * FROM papers WHERE "

    # first = True

    str_topic = ['', '']
    str_author = ['', '']

    # Include line for topic, radio "Any" is not checked
    # -> AND query
    if topic_entries[0]:

        words = [word.strip() for word in topic_entries[0].split(",")]
        words = [queryString(word) for word in words]

        if radio_states[0]:
            operator = 'OR'
        else:
            operator = 'AND'

        for word in words:
            if word == words[0]:
                str_topic[0] = "topic_simple LIKE '{}'".format(word)
            else:
                str_topic[0] += " {} topic_simple LIKE '{}'".format(operator, word)

    # TOPIC, NOT condition
    if topic_entries[1]:
        words = [word.strip() for word in topic_entries[1].split(",")]
        words = [queryString(word) for word in words]

        for word in words:
            if word == words[0]:
                str_topic[1] = "topic_simple NOT LIKE '{}'".format(word)
            else:
                str_topic[1] += " AND topic_simple NOT LIKE '{}'".format(operator, word)


    # AUTHOR, AND/OR condition
    if author_entries[0]:

        words = [word.strip() for word in author_entries[0].split(",")]
        words = [queryString(word) for word in words]

        if radio_states[2]:
            operator = 'OR'
        else:
            operator = 'AND'

        for word in words:
            if word == words[0]:
                str_author[0] = "' ' || replace(authors, ',', ' ') || ' ' LIKE '{}'".format(word)
            else:
                str_author[0] += " {} ' ' || replace(authors, ',', ' ') || ' ' LIKE '{}'".format(operator, word)

    # AUTHOR, NOT condition
    if author_entries[1]:

        words = [word.strip() for word in author_entries[1].split(",")]
        words = [queryString(word) for word in words]

        for word in words:
            if word == words[0]:
                str_author[1] = "' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{}'".format(word)
            else:
                str_author[1] += " {} ' ' || replace(authors, ',', ' ') || ' ' NOT LIKE '{}'".format(operator, word)


    # Build the query from the parts. Concatenate them with AND
    concatenate = [element for element in str_topic + str_author if element]
    for element in concatenate:
        if element is concatenate[0]:
            base += "(" + element + ")"
        else:
            base += " AND (" + element + ")"

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
