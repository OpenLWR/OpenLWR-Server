import json
from server.server_events import server_chat_event

def handle(data, source_user):
    server_chat_event.fire("{1}: {0}".format(data, source_user))
