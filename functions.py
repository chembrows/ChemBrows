#!/usr/bin/python
# coding: utf-8


import sys
import os
import arrow
import re
import constants


def prettyDate(str_date: str) -> str:

    """
    Prettify a date. Ex: 3 days ago

    Arguments:
        str_date (str): date to prettify. Normally YYYY-MM-DD

    Returns:
        str: the prettyfied date
    """

    now = arrow.now()
    date = arrow.get(str_date)

    if now.timestamp - date.timestamp < 86400:
        return "Today"
    else:
        return date.humanize(now.naive)


def simpleChar(rubbish_str: str, wildcards: bool = True) -> str:

    """
    Slugify a string, i.e. remove special characters like accents

    Arguments:
        rubbish_str (str): the str to slugify
        wildcards (bool): if False, don't slugify wildcards (*). Otherwise, do

    Returns:
        str: the sluggified string

    http://www.siteduzero.com/forum-83-810635-p1-sqlite-recherche-avec-like-insensible-a-la-casse.html#r7767300
    http://stackoverflow.com/questions/35382793/regex-match-all-special-characters-but-not
    """

    resource_dir, _ = getRightDirs()

    with open(os.path.join(resource_dir, 'config/data.bin'), 'rb') as f:
        _replaces = f.read().decode('utf8').split('\x00')

    rubbish_str = rubbish_str.lower()

    chars = []
    for ch in rubbish_str:
        if ch == '*' and not wildcards:
            chars.append('*')
            continue

        codepoint = ord(ch)

        if not codepoint:
            chars.append('\x00')
            continue

        try:
            chars.append(_replaces[codepoint - 1])
        except IndexError:
            pass

    rubbish_str = "".join(chars)

    return re.sub(r'_|[^\w\s*]+', ' ', rubbish_str)


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

    str_topic = ['', '']
    str_author = ['', '']

    # Include line for topic, radio "Any" is not checked
    # -> AND query
    if topic_entries[0]:

        words = [simpleChar(word.strip(), False) for word
                 in topic_entries[0].split(",")]

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

        words = [simpleChar(word.strip(), False) for word
                 in topic_entries[1].split(",")]

        words = [queryString(word) for word in words]

        for word in words:
            if word == words[0]:
                str_topic[1] = "topic_simple NOT LIKE '{}'".format(word)
            else:
                str_topic[1] += " AND topic_simple NOT LIKE '{}'".format(word)


    # AUTHOR, AND/OR condition
    if author_entries[0]:

        words = [simpleChar(word.strip(), False) for word
                 in author_entries[0].split(",")]

        words = [queryString(word) for word in words]

        if radio_states[2]:
            operator = 'OR'
        else:
            operator = 'AND'

        for word in words:
            if word == words[0]:
                str_author[0] = " author_simple LIKE '{}'".format(word)
            else:
                str_author[0] += " {} author_simple LIKE '{}'".format(operator, word)

    # AUTHOR, NOT condition
    if author_entries[1]:

        words = [simpleChar(word.strip(), False) for word
                 in author_entries[1].split(",")]

        words = [queryString(word) for word in words]

        for word in words:
            if word == words[0]:
                str_author[1] = " author_simple NOT LIKE '{}'".format(word)
            else:
                str_author[1] += " AND author_simple NOT LIKE '{}'".format(word)


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


def getRightDirs():

    """Get the DATA_PATH and the resource_dir pathes.
    DATA_PATH is on the user side if CB is frozen"""

    if getattr(sys, "frozen", False):
        # resource_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        resource_dir = sys._MEIPASS
        DATA_PATH = constants.DATA_PATH
    else:
        resource_dir = '.'
        DATA_PATH = '.'

    return resource_dir, DATA_PATH


def getVersion():

    """Get the ChemBrows' version"""

    resource_dir, DATA_PATH = getRightDirs()

    with open(os.path.join(resource_dir, 'config/version.txt'),
              'r', encoding='utf-8') as version_file:

        version = version_file.read().strip()

    return version


if __name__ == "__main__":
    print(prettyDate("2018-10-15"))
    # like(10)
    # _, dois = listDoi()
    # print(dois)
    # queryString("sper**mine")
    # queryString("*sperm*")
    # queryString("spermine")
    # checkData()

    # match(['jean-patrick francoia', 'robert pascal', 'laurent vial'], "r* pascal")

    # unidecodePerso('test')
    # print(simpleChar("Her_%%%v*é Cottet", False))
    # queryString("Hervé Cottet")
    # simpleChar("C* N. hunter", False)
    pass
