#!/usr/bin/python
# coding: utf-8

import functions as fct
from log import MyLog


l = MyLog("output_tests_functions.log", mode="w")
l.debug("---------------------- START NEW RUN OF TESTS ----------------------")


def logAssert(test, msg):

    """Function to log the result of an assert
    http://stackoverflow.com/questions/24892396/py-test-logging-messages-and-test-results-assertions-into-a-single-file
    """

    if not test:
        l.error(msg)
        assert test, msg


def test_query_string():

    logAssert(
        fct.queryString("sper*mine") == "% sper%mine %", "queryString, test 1 failed"
    )

    logAssert(fct.queryString("*sperm*") == "%sperm%", "queryString, test 2 failed")

    logAssert(
        fct.queryString("spermine") == "% spermine %", "queryString, test 3 failed"
    )


def test_remove_html():

    logAssert(fct.removeHtml("<a>coucou</a>") == "coucou", "removeHtml failed")


def test_simple_char():

    logAssert(
        fct.simpleChar("C* N. hunter") == "c* n  hunter", "simpleChar, test 1 failed"
    )

    logAssert(
        fct.simpleChar("C* N. hunter") == "c* n  hunter", "simpleChar, test 2 failed"
    )

    logAssert(
        fct.simpleChar("Her_%%%v*é Cottet") == "her  v*e cottet",
        "simpleChar, test 3 failed",
    )

    logAssert(fct.simpleChar("are you ø") == "are you o", "simpleChar, test 5 failed")

    logAssert(
        fct.simpleChar("are you here?") == "are you here ", "simpleChar, test 6 failed"
    )


if __name__ == "__main__":
    pass
