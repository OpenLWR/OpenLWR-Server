# colors
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

import config

hook = None

logging.basicConfig(    format='[%(asctime)s] %(levelname)s - %(message)s',
    level=logging.DEBUG if config.config["debug"] else logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()

def debug(message:str,color:str = None):
    """message, *color"""
    if color:
        message = color + message + ENDC
    logger.debug(message)

def info(message:str,color:str = None):
    """message, *color"""
    if color:
        message = color + message + ENDC
    logger.info(message)

def warning(message:str,color:str = None):
    """message, *color"""

    if color:
        message = color + message + ENDC

    # TODO: add option for logging to other external services(datadog, etc)
    logger.warning(message)

def error(message:str,color:str = None):
    """message, *color"""

    if color:
        message = color + message + ENDC

    # TODO: add option for logging to other external services(datadog, etc)
    logger.error(message)