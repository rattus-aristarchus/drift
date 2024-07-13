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


conf_path = os.path.dirname(sys.path[0]) + "/conf.yml"
CONF = conf.init_conf(conf_path)
CONST = []


# STRINGS = yaml.safe_load(open(MAIN_DIR + "/strings.yml", "r", encoding="utf-8"))


def set_conf(name, value):
    CONF[name] = value
    with open(conf_path, "w", encoding="utf-8") as file:
        yaml.dump(CONF, file)
