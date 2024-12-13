import json
from simulation.init_simulation import simulation as sim
from server.server_events import server_chat_event
def handle(data, user):
    server_chat_event.fire("{1}: {0}".format(data, user.username))
    ip = user.websocket.remote_address[0]
    if ip == "127.0.0.1" and data[0] == "/":
        parse_command(data[1:])
    
def change_pause(value):
    sim.running = value
    if sim.running:
        server_chat_event.fire("Simulation unpaused.")
    else:
        server_chat_event.fire("Simulation paused.")
    
def parse_command(cmd):
    match cmd:
        case "pause":
            change_pause(not sim.running)
