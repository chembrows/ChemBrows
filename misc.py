#!/usr/bin/python
# coding: utf-8

import sqlite3

# Fct de test uniquement
def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("debug/test.sqlite")
    bdd.row_factory = sqlite3.Row
    c = bdd.cursor()

    c.execute("SELECT id, abstract FROM papers")

    results = c.fetchall()

    for line in results:
        c.execute("UPDATE papers SET percentage_match = ? WHERE id = ?")
    c.close()
    bdd.close()



# if __name__ == "__main__":
    # pass

