#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import yaml
import os
import sys

from src.io import conf
from kivy.logger import Logger

# getcwd returns the current working directory, which can change during program execution,
# and which can give different results depending on where the program is launched from. for
# now, sys.path[0] is a better alternative, it gives the initial directory from which the
# script was launched

# MAIN_DIR = os.path.dirname(os.getcwd())
# MAIN_DIR = os.path.dirname(sys.path[0])
MAIN_DIR = os.getcwd()
RES_DIR = os.path.join(MAIN_DIR, "res")
Logger.info("Storage: loading dir " + MAIN_DIR)
ASSETS_DIR = os.path.join(RES_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
NAMESPACES_DIR = os.path.join(RES_DIR, "namespaces")

conf_path = MAIN_DIR + "/conf.yml"
CONF = conf.init_conf(conf_path)


# STRINGS = yaml.safe_load(open(MAIN_DIR + "/strings.yml", "r", encoding="utf-8"))


def set_conf(name, value):
    CONF[name] = value
    with open(conf_path, "w", encoding="utf-8") as file:
        yaml.dump(CONF, file)
