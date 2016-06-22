#!/usr/bin/python
# coding: utf-8

from PyQt4 import QtCore


class LittleThread(QtCore.QThread):

    """Create a personal thread API, to spawn a thread with
    any function and its parameters"""

    # https://joplaete.wordpress.com/2010/07/21/threading-with-pyqt4/
    # http://stackoverflow.com/questions/34496313/display-busy-progressbar-for-long-process-no-thread/34496585#34496585

    def __init__(self, function, *args, **kwargs):

        QtCore.QThread.__init__(self)

        self.function = function
        self.args = args
        self.kwargs = kwargs


    def run(self):

        self.function(*self.args, **self.kwargs)
        return
