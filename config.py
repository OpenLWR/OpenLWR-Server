import os
import config
import shutil
import json
import log

config = None

if config == None:
    try:
        if not os.path.isfile("config.json"):
            log.info("Config file not found, creating.")
            shutil.copy("config.example.json", "config.json")

        with open("config.json") as config_file:
            config = json.load(config_file)

    except Exception as e:
        log.error(f"Failed to load config file: {e}")
