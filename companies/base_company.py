#!/usr/bin/python
# coding: utf-8

import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from log import MyLog


class BaseCompany():

    def __init__(self, url: str) -> None:

        self.l = MyLog("activity.log")
        self.url = url

        pass


if __name__ == '__main__':
    company_obj = BaseCompany("http://feeds.feedburner.com/acs/jcisd8")
    pass
