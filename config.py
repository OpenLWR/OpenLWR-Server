import os
import config
import shutil
import json
import log

config = None

if config == None:
    try:
        if not os.path.isfile("config.json"):
            log.info("Config file not found, creating")
            shutil.copy("config.example.json", "config.json")

        with open("config.json") as config_file:
            config = json.load(config_file)

        if not os.path.isdir("simulation/models/%s" % config["model"]):
            log.error("The configured model directory does not exist.")
            exit()
        
        if not os.path.isfile("simulation/models/%s/model.py" % config["model"]):
            log.error("The configured model has a directory but no model.py. Did you misspell model.py?")
            exit()

        log.info("The config initialized sucessfully.")


    except Exception as e:
        log.error(f"Failed to load config file: {e}")
