import json

def handle(data):
    switches_updated = json.loads(data)
    print(switches_updated)