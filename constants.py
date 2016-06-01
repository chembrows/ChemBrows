#!/usr/bin/python
# coding: utf-8

from appdirs import AppDirs


dirs = AppDirs("ChemBrows", "ChemBrows")
DATA_PATH = dirs.user_config_dir

# appname = "SuperApp"
# appauthor = "Acme"
# user_data_dir(appname, appauthor)

# Data dir for Max, Windows and Linux
# '/Users/trentm/Library/Application Support/ChemBrows'
# 'C:\\Users\\trentm\\AppData\\Local\\Acme\\ChemBrows'
# '/home/trentm/.config/superapp

# Tweets are 140 characters long
LEN_TWEET = 140
