import uuid
import traceback
import websockets
from server.connection_manager import manager
from server.server_events import server_user_logout_event
from server.constants import packets
from server.helpers import packet_helper
from server.client_events import client_switch_parameters_update_event
from server.server_events import server_switch_parameters_update_event
from server.client_events import client_button_parameters_update_event
from server.server_events import server_button_parameters_update_event
from server.server_events import server_player_position_parameters_update_event
from server.client_events import client_player_position_parameters_update_event
from server.server_events import server_rod_position_parameters_update_event
from server.client_events import client_rod_select_update_event
from server.server_events import server_chat_event
from server.client_events import client_chat_event
from server.client_events import client_voip_event
from server.client_events import client_recorder_parameters_update_event
from server.server_events import server_recorder_parameters_update_event
from server.server_events import server_meter_parameters_update_event
import json
import importlib
import copy
import time
from server import rcon
rcon_init = False

def init_server(websocket):
    import log
    import config
    if not rcon_init:
        rcon.init()

    login_step = 0
    model_copy = None

    try:
        for packet in websocket:
            try:
                if login_step == 0:
                    token_str = str(uuid.uuid4())
                    packet_id, packet_data = packet_helper.parse(packet)

                    login_parameters = json.loads(packet_data)

                    username = login_parameters["username"]
                    version = login_parameters["version"]

                    # check the packet is the correct type and the username is valid
                    assert packet_id == packets.ClientPackets.USER_LOGIN, "Client sent an invalid packet while logging in."
                    assert (len(username) <= 20 and len(username) >= 2), "Client has an invalid username."

                    # check to make sure the client has the same version as the server
                    assert version == config.config["version"], f"Version mismatch. Client has {version} - Server has {config.config["version"]}"

                    login_step += 1

                #before logging in the client, we need to actually give them all the data
                #make a copy of the current state of model.py

                    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")

                    recorders = {}
                    model_recorders = model.recorders.copy()
                    for recorder in model_recorders:
                        recorders[recorder] = {
                            "channels":model_recorders[recorder].channels,
                            "buttons":model_recorders[recorder].buttons,
                            "page":model_recorders[recorder].page,
                            "elements":model_recorders[recorder].elements,
                            "display_on":model_recorders[recorder].display_on,
                        }

                    model_rods = copy.deepcopy(model.rods) #sanitize rods sent to the client
                    for rod in model_rods:
                        model_rods[rod].pop("neutrons")
                        model_rods[rod].pop("measured_neutrons_last")
                        model_rods[rod].pop("measured_neutrons")
                        model_rods[rod].pop("driftto")
                        model_rods[rod].pop("driving")
                        model_rods[rod].pop("reed_switch_fail")
                        model_rods[rod].pop("accum_pressure")

                    model_copy = {
                        "switches" : model.switches.copy(),
                        #"values" : model.values.copy(), #This will stay on the client
                        "buttons" : model.buttons.copy(),
                        #"indicators" : model.indicators.copy(), #This will stay on the client
                        "alarms" : model.alarms.copy(),
                        "rods" : model_rods,
                        "recorders" : recorders,
                    }

                if login_step > 0:
                    if login_step <= 5:
                        i = 1
                        for table_name in model_copy:
                            if i == login_step:
                                info = model_copy[table_name]

                                data_to_send = f"{json.dumps(info)}|{json.dumps(table_name)}" #Do we actually need to json.dumps the table name?

                                websocket.send(packet_helper.build(packets.ServerPackets.DOWNLOAD_DATA,data_to_send))
                                break
                            i+=1
                    else:

                        #TODO: Checksum the client against the server

                        #last, we finally broadcast the login packet
                        websocket.send(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK,"ok"))

                        token_object = manager.connect(websocket, token_str)
                        manager.set_username(token_str, username)
                        break
                    login_step+=1
                

            except AssertionError as msg:
                # login invalid
                log.warning(f"User login failed for {msg}")
                manager.send_user_packet(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK,str(msg)),token_object.token)
                manager.disconnect(token_str)

            except Exception:
                # exception in login
                log.error(traceback.format_exc())

    except websockets.exceptions.ConnectionClosedError:
        log.info("Connection closed.")
        return #this works but should we do this?
        

    try:
        for packet in websocket:
            packet_id, packet_data = packet_helper.parse(packet)
            match packet_id:
                case packets.ClientPackets.SWITCH_PARAMETERS_UPDATE:
                    client_switch_parameters_update_event.handle(packet_data)
                    log.blame(token_object.username,packet_data)

                case packets.ClientPackets.BUTTON_PARAMETERS_UPDATE:
                    client_button_parameters_update_event.handle(packet_data)
                    log.blame(token_object.username,packet_data)

                case packets.ClientPackets.PLAYER_POSITION_PARAMETERS_UPDATE:
                    client_player_position_parameters_update_event.handle(packet_data,token_object)

                case packets.ClientPackets.ROD_SELECT_UPDATE:
                    client_rod_select_update_event.handle(packet_data)
                    log.blame(token_object.username,packet_data)

                case packets.ClientPackets.SYNCHRONIZE: #allows the client to request some extra stuff
                    server_player_position_parameters_update_event.fire_initial(token_object.token)
                    server_meter_parameters_update_event.fire_initial(token_object.token)

                case packets.ClientPackets.CHAT:
                    client_chat_event.handle(packet_data, token_object.username)

                case packets.ClientPackets.VOIP:
                    client_voip_event.handle(packet_data, token_object.username)

                case packets.ClientPackets.RCON:
                    rcon.process_rcon(packet_data)

                case packets.ClientPackets.RECORDER:
                    client_recorder_parameters_update_event.handle(packet_data)

    except websockets.exceptions.ConnectionClosedOK:
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
    except Exception:
        log.error(traceback.format_exc())
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
