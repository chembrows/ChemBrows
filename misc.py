#!/usr/bin/python
# coding: utf-8

import sqlite3
import functions


# Fct de test uniquement
def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("fichiers.sqlite")
    bdd.row_factory = sqlite3.Row
    c = bdd.cursor()

    c.execute("SELECT * FROM papers")

    results = c.fetchall()

    for line in results:
        id_bdd = line['id']
        authors = line['authors']
        print(id_bdd)

        if authors is not None and authors != '':
            topic_simple = line['topic_simple'] + functions.simpleChar(authors)
            c.execute("UPDATE papers SET topic_simple = ? WHERE id = ?", (topic_simple, id_bdd))

    bdd.commit()
    c.close()
    bdd.close()


if __name__ == "__main__":
    checkData()
    pass
