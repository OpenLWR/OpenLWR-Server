import config
import importlib
model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")

def getVal(cmd:str):

    #Goes : Action Area Value

    assert cmd[1] in areas, "Specified area does not exist."
    assert cmd[2] in areas[cmd[1]], "Specified value in area does not exist."

    return areas[cmd[1]][cmd[2]]

areas = {
    "switches" : model.switches,
}

actions = {
    "getVal" : getVal
}

def process_rcon(data):
    #I havent got a chance to test this or implement it clientside
    try:

        assert config.config["debug"], "The server is not in debug mode."

        cmd = data

        cmd = cmd.lower() #non case-sensitive
        cmd = cmd.split(" ") #split at the spaces
        if cmd[0] in actions:
            #return actions[cmd[0]](cmd)
            val = actions[cmd[0]](cmd)

    except AssertionError as msg:
        #invalid
        print(msg)

    except Exception as e:
        print(e)