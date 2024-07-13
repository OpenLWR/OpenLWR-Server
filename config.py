import os
import config
import shutil
import json

config = None

if config == None:
    try:
        if not os.path.isfile("config.json"):
            print("Config file not found, creating")
            shutil.copy("config.example.json", "config.json")

        with open("config.json") as config_file:
            config = json.load(config_file)

        if not os.path.isdir("simulation/models/%s" % config["model"]):
            print("The configured model directory does not exist.")
            exit()
        
        if not os.path.isfile("simulation/models/%s/model.py" % config["model"]):
            print("The configured model has a directory but no model.py. Did you misspell model.py?")
            exit()

        print("The config initialized sucessfully.",log.BLUE)


    except Exception as e:
        print(f"Failed to load config file: {e}")
