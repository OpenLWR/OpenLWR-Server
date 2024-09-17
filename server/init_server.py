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
from server.server_events import server_recorder_parameters_update_event
import json
import importlib
from server import rcon
rcon_init = False


def init_server(websocket):
    import log
    import config
    if not rcon_init:
        rcon.init()
    for packet in websocket:
        try:
            token_str = str(uuid.uuid4())
            packet_id, packet_data = packet_helper.parse(packet)

            login_parameters = json.loads(packet_data)

            username = login_parameters["username"]
            version = login_parameters["version"]

            token_object = manager.connect(websocket, token_str)
            manager.set_username(token_str, username)

            # check the packet is the correct type and the username is valid
            assert packet_id == packets.ClientPackets.USER_LOGIN, "Client sent an invalid packet while logging in."
            assert (len(username) <= 20 and len(username) >= 2), "Client has an invalid username."

            # check to make sure the client has the same version as the server
            assert version == config.config["version"], f"Version mismatch. Client has {version} - Server has {config.config["version"]}"

            #before logging in the client, we need to actually give them all the data
            #make a copy of the current state of model.py

            model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")

            recorders = {}
            model_recorders = model.recorders.copy()
            for recorder in model_recorders:
                recorders[recorder] = {
                    "channels":model_recorders[recorder].channels,
                }

            model_copy = {
                "switches" : model.switches.copy(),
                #"values" : model.values.copy(), #This will stay on the client
                "buttons" : model.buttons.copy(),
                #"indicators" : model.indicators.copy(), #This will stay on the client
                "alarms" : model.alarms.copy(),
                "rods" : server_rod_position_parameters_update_event.old_rods.copy(),
                "recorders" : recorders,
            }

            for table_name in model_copy:
                info = model_copy[table_name]

                data_to_send = f"{json.dumps(info)}|{json.dumps(table_name)}" #Do we actually need to json.dumps the table name?

                manager.send_user_packet(packet_helper.build(packets.ServerPackets.DOWNLOAD_DATA,data_to_send),token_object.token)
            
            #TODO: Checksum the client against the server

            #last, we finally broadcast the login packet
            manager.send_user_packet(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK,"ok"),token_object.token)
            break

        except AssertionError as msg:
            # login invalid
            log.warning(f"User login failed for {msg}")
            manager.send_user_packet(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK,str(msg)),token_object.token)
            manager.disconnect(token_str)

        except Exception:
            # exception in login
            log.error(traceback.format_exc())

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

                case packets.ClientPackets.SYNCHRONIZE: #allows the client to request all the simulation data, like how it was when they joined the server.
                    server_switch_parameters_update_event.fire_initial(token_object.token)
                    server_button_parameters_update_event.fire_initial(token_object.token)
                    server_player_position_parameters_update_event.fire_initial(token_object.token)
                    server_rod_position_parameters_update_event.fire_initial(token_object.token)

                case packets.ClientPackets.CHAT:
                    client_chat_event.handle(packet_data, token_object.username)

                case packets.ClientPackets.RCON:
                    rcon.process_rcon(packet_data)

                case packets.ClientPackets.RECORDER:
                    log.info("Client tried to use a packet that is not handled yet.")

    except websockets.exceptions.ConnectionClosed:
        log.info(f"User {token_object.username} disconnected")
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
    except Exception:
        log.error(traceback.format_exc())
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
