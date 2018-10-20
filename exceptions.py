#!/usr/bin/python
# coding: utf-8


class CBError(Exception):

    pass


class WorkerError(CBError):

    pass


class DownloadError(WorkerError):

    pass


class JournalError(WorkerError):

    pass


if __name__ == '__main__':
    pass
