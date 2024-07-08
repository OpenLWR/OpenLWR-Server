# TODO: colors
PINK = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

import logging

import json

try:
    config = json.load(open("config.json"))
except:
    config = {"debug" : False} #if we cant get config.json, we just cry about it and wait for the config.py to error out



logging.basicConfig(    format='[%(asctime)s] %(levelname)s - %(message)s',
    level=logging.DEBUG if config["debug"] else logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()

def debug(message):
    logger.debug(message)

def info(message):
    logger.info(message)

def warning(message):
    # TODO: add option for logging to an external service (discord, datadog, etc)
    logger.warning(message)

def error(message):
    # TODO: add option for logging to an external service (discord, datadog, etc)
    logger.error(message)
