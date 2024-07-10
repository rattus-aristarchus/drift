#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import yaml
import os
import sys

import conf
from kivy.logger import Logger

# getcwd returns the current working directory, which can change during program execution,
# and which can give different results depending on where the program is launched from. for
# now, sys.path[0] is a better alternative, it gives the initial directory from which the
# script was launched

# MAIN_DIR = os.path.dirname(os.getcwd())
MAIN_DIR = os.path.dirname(sys.path[0])
Logger.info("Util: using dir " + MAIN_DIR)


conf_path = MAIN_DIR + "/conf.yml"
CONF = conf.init_conf(conf_path)


data_dir = os.path.join(MAIN_DIR, "res")
CONST = yaml.safe_load(open(data_dir + "/const.yml", "r", encoding="utf-8"))
worlds_dir = os.path.join(data_dir, "worlds")
WORLDS = {}

for element in os.listdir(worlds_dir):
    element_path = os.path.join(worlds_dir, element)
    if os.path.isfile(element_path) and os.path.splitext(element)[1] == ".yml":
        world = yaml.safe_load(open(element_path, "r", encoding="utf-8"))
        world_name = os.path.splitext(element)[0]
        WORLDS[world_name] = world

# STRINGS = yaml.safe_load(open(MAIN_DIR + "/strings.yml", "r", encoding="utf-8"))


def set_conf(name, value):
    CONF[name] = value
    with open(MAIN_DIR + "/conf.yml", "w", encoding="utf-8") as file:
        yaml.dump(CONF, file)
