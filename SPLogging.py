# Copyright (c) 2010 stas zytkiewicz stas@childsplay.mobi
#


# provides a logging object
# All modules get the same logger so this must called asap

__author__ = 'stas'
import logging
import sys

# Added custom loglevel as various parts of kivy also using it
import time
import logging.handlers
import os
from copy import copy

def _make_dirs(p):
    if not os.path.exists(p):
        os.makedirs(p)

HOMEDIR = sys.path[0]
LOGDIR = os.path.join(HOMEDIR, 'logs')
_make_dirs(LOGDIR)

ERRORLOGDIR = os.path.join(LOGDIR, 'Errors')
_make_dirs(ERRORLOGDIR)

LOGPATH = os.path.join(LOGDIR, 'bt_kivy.log')

print(("HOMEDIR set to: %s" % HOMEDIR))

use_color =True

# Color logging taken from the kivy logger
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(range(8))

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'TRACE': YELLOW,
    'WARNING': MAGENTA,
    'INFO': BLUE,
    'DEBUG': CYAN,
    'CRITICAL': RED,
    'ERROR': RED}

CONSOLELOGLEVEL = logging.DEBUG
FILELOGLEVEL = logging.DEBUG

class ColoredFormatter(logging.Formatter):

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        col_record = copy(record)
        levelname = col_record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ)
            col_record.levelname = levelname_color
        return logging.Formatter.format(self, col_record)


# set loglevel, possible values:
# logging.DEBUG
# logging.INFO
# logging.WARNING
# logging.ERROR
# logging.CRITICAL

def set_level(level):
    global CONSOLELOGLEVEL, FILELOGLEVEL
    lleveldict = {'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL}
    if level not in lleveldict:
        print(("Invalid loglevel: %s, setting loglevel to 'debug'" % level))
        llevel = lleveldict['debug']
    else:
        llevel = lleveldict[level]
    CONSOLELOGLEVEL = llevel
    FILELOGLEVEL = llevel


def start():
    global CONSOLELOGLEVEL, FILELOGLEVEL
    # create logger
    logger = logging.getLogger("bt")
    logger.handlers.clear()  # Clear existing handlers
    logger.setLevel(CONSOLELOGLEVEL)

    # create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(CONSOLELOGLEVEL)

    # create file handler and set level
    fh = logging.handlers.RotatingFileHandler(LOGPATH, maxBytes=10485760, backupCount=5, encoding='utf8')
    fh.setLevel(FILELOGLEVEL)

    # create formatter
    msg = u"[%(levelname)-7s]-%(asctime)s-%(name)s:%(lineno)d > %(message)s"
    color_msg = u"[%(levelname)-7s]-%(asctime)s-%(name)s:%(lineno)d > %(message)s"
    k_msg = u"[%(levelname)-7s]-%(asctime)s-%(name)s: %(message)s"

    # add formatter to ch and fh
    ch.setFormatter(ColoredFormatter(color_msg, use_color=use_color))
    fh.setFormatter(logging.Formatter(msg))

    # add ch and fh to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info("logger created: %s" % LOGPATH)

    # test
    module_logger = logging.getLogger("bt.SPLogging")
    module_logger.info("******************************")
    module_logger.info(f"** {time.asctime()} **")
    module_logger.info("******************************")
    module_logger.info(f"logger created, start logging to {LOGPATH}")
    module_logger.info(f"sys.path: {sys.path}")


