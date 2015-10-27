#!/usr/bin/python
# coding: utf-8

import os
from appdirs import AppDirs


dirs = AppDirs("ChemBrows", "ChemBrows")
DATA_PATH = dirs.user_config_dir

# appname = "SuperApp"
# appauthor = "Acme"
# user_data_dir(appname, appauthor)

# Data dir for Max, Windows and Linux
# '/Users/trentm/Library/Application Support/SuperApp'
# 'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp'
# '/home/trentm/.config/superapp



# Setting for the size of the icons
DIMENSION = 35

# Tweets are 140 characters long
LEN_TWEET = 140
