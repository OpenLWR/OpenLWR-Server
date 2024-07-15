
PINK = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

import logging
from dhooks import Webhook, File, Embed #this util allows us to log to discord easily

import json

import config

hook = None

if config.config["discord_webhook_logging"] != "":
    hook = Webhook(config.config["discord_webhook_logging"])



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

    if hook != None:
        embed = Embed(title = "Warning",description = message,timestamp = "now",color=0xFFA500)
        hook.send(embed=embed)

    if color:
        message = color + message + ENDC

    # TODO: add option for logging to other external services(datadog, etc)
    logger.warning(message)

def error(message:str,color:str = None):
    """message, *color"""

    #TODO: not all errors are sent because they arent sent through log.py. Is there a way to include them?
    if hook != None:
        embed = Embed(title = "Error",description = message,timestamp = "now",color=0xFF0000)
        hook.send(embed=embed)

    if color:
        message = color + message + ENDC


    # TODO: add option for logging to other external services(datadog, etc)
    logger.error(message)

def blame(user,message): #TODO: More elegant way of doing this?
    if config.config["blame_logging"]:
        print("Server blames %s for  %s" % (user,message))
