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

    c.execute("SELECT * FROM papers WHERE graphical_abstract is NULL")

    results = c.fetchall()

    for line in results:
        id_bdd = line['id']
        graphical = line['graphical_abstract']
        print(graphical)

        if graphical is None:
            graphical = 'Empty'
            c.execute("UPDATE papers SET graphical_abstract = ? WHERE id = ?", (graphical, id_bdd))

    bdd.commit()
    c.close()
    bdd.close()


if __name__ == "__main__":
    checkData()
    pass
