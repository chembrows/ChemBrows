#!/usr/bin/python
# coding: utf-8

import sqlite3
import functions
import fnmatch


# TEST FUNCTION ONLY. NOT USED IN THE CODE
def checkData():

    """Fct de test uniquement"""

    bdd = sqlite3.connect("fichiers.sqlite")
    bdd.row_factory = sqlite3.Row
    c = bdd.cursor()

    c.execute("CREATE TABLE results AS SELECT * FROM papers WHERE journal='J. Chromatogr. A'")
    # c.execute("SELECT * FROM papers WHERE graphical_abstract is NULL")

    # results = c.fetchall()

    # for line in results:
        # id_bdd = line['id']
        # graphical = line['graphical_abstract']
        # print(graphical)

        # if graphical is None:
            # graphical = 'Empty'
            # c.execute("UPDATE papers SET graphical_abstract = ? WHERE id = ?", (graphical, id_bdd))

    # bdd.commit()
    c.close()
    bdd.close()

def testAuthors(input):

    author_entries = ['', 'Thomas* Pinto', '']

    authors = input.split(', ')
    authors = [element.lower() for element in authors]
    print(authors)
    print("\n")

    adding = True
    list_adding_or = []

    # Loop over the 3 kinds of condition: AND, OR, NOT
    for index, entries in enumerate(author_entries):

        if not entries:
            continue

        print(entries.split(','))

        # For each person in the SQL query
        for person in entries.split(','):

            # Normalize the person's string
            person = person.strip().lower()

            if '*' in person:
                matching = fnmatch.filter(authors, person)
                if matching:
                    list_adding_or.append(True)
                    break
            else:
                # Tips for any()
                # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
                # if any(person in element for element in authors):
                if person in authors:
                    list_adding_or.append(True)
                else:
                    list_adding_or.append(False)

        print("list_adding_or:", list_adding_or)





if __name__ == "__main__":
    # checkData()
    testAuthors("Thomas C. Eadsforth, Andrea Pinto, Rosaria Luciani, Lucia Tamborini, Gregorio Cullia, Carlo De Micheli, Luciana Marinelli, Sandro Cosconati, Ettore Novellino, Leonardo Lo Presti, Anabela Cordeiro da Silva, Paola Conti, William N. Hunter, Maria P. Costi")
    pass
