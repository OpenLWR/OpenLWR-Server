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

def init_server(websocket):
    for packet in websocket:
        try:
            packet_id, packet_data = packet_helper.parse(packet)
            if packet_id != packets.ClientPackets.USER_LOGIN:
                raise Exception("User login packet invalid.")
            username = packet_data
            print(len(username))
            if len(username) <= 20 and len(username) >= 2:
                token_str = str(uuid.uuid4())
                token_object = manager.connect(websocket, token_str)
                manager.set_username(token_str, username)
                manager.broadcast_packet(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK, ""))
                break
            else:
                raise Exception("Username invalid.")
        except Exception as e: 
            print(e)
            manager.disconnect(token_str)

    # inform the client of all switch positions
    server_switch_parameters_update_event.fire_initial(token_str)
    # do the same for all button positions
    server_button_parameters_update_event.fire_initial(token_str)

    server_player_position_parameters_update_event.fire_initial(token_str)

    server_rod_position_parameters_update_event.fire_initial(token_str)
    
    for packet in websocket:
        try:
            #print(packet) # TODO: proper logging system

            packet_id, packet_data = packet_helper.parse(packet)

            if packet_id == packets.ClientPackets.SWITCH_PARAMETERS_UPDATE:
                client_switch_parameters_update_event.handle(packet_data)
            elif packet_id == packets.ClientPackets.BUTTON_PARAMETERS_UPDATE:
                client_button_parameters_update_event.handle(packet_data)
            elif packet_id == packets.ClientPackets.PLAYER_POSITION_PARAMETERS_UPDATE:
                client_player_position_parameters_update_event.handle(packet_data,token_object.username)
            elif packet_id == packets.ClientPackets.ROD_SELECT_UPDATE:
                client_rod_select_update_event.handle(packet_data)
        except websockets.exceptions.ConnectionClosed:
            print("client disconnected%s" % token_object.username)
            manager.disconnect(token_str)
            server_user_logout_event.fire(token_object.username)
        except Exception:
            print(traceback.format_exc())
            manager.disconnect(token_str)
            server_user_logout_event.fire(token_object.username)
