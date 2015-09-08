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

    c.execute("SELECT * FROM papers WHERE journal='Chem. Asian j.'")

    results = c.fetchall()

    for line in results:
        id_bdd = line['id']

        c.execute("UPDATE papers SET journal = 'Chem. Asian J.' WHERE id = ?", (id_bdd,))

    bdd.commit()
    c.close()
    bdd.close()


if __name__ == "__main__":
    checkData()
    pass
