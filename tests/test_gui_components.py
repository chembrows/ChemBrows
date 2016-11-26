#!/usr/bin/python
# coding: utf-8


"""
Test module to be ran with pytest.

Start the tests with something like this:
py.test -xs test_hosts.py -k getData
"""


import os
import pytest

from log import MyLog
from advanced_search import AdvancedSearch
from wizard_journal import WizardJournal


l = MyLog("output_tests_gui_components.log", mode='w')
l.debug("---------------------- START NEW RUN OF TESTS ----------------------")


def logAssert(test, msg):

    """Function to log the result of an assert
    http://stackoverflow.com/questions/24892396/py-test-logging-messages-and-test-results-assertions-into-a-single-file
    """

    if not test:
        l.error(msg)
        assert test, msg


def test_WizardJournal(qtbot):

    test = WizardJournal()
    qtbot.addWidget(test)



if __name__ == "__main__":
    test_WizardJournal()
