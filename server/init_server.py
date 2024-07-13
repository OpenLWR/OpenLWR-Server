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


def init_server(websocket):
    import log
    for packet in websocket:
        try:
            token_str = str(uuid.uuid4())
            packet_id, packet_data = packet_helper.parse(packet)

            login_parameters = json.loads(packet_data)

            username = login_parameters["username"]

            # check the packet is the correct type and the username is valid
            assert packet_id == packets.ClientPackets.USER_LOGIN
            assert not len(username) <= 20 and len(username) >= 2

            username = packet_data
            token_object = manager.connect(websocket, token_str)
            manager.set_username(token_str, username)
            manager.broadcast_packet(packet_helper.build(packets.ServerPackets.USER_LOGIN_ACK))
            break

        except AssertionError:
            # login invalid
            log.warning(f"User login failed.")
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
                    client_player_position_parameters_update_event.handle(packet_data,token_object.username)

                case packets.ClientPackets.ROD_SELECT_UPDATE:
                    client_rod_select_update_event.handle(packet_data)
                    log.blame(token_object.username,packet_data)

                case packets.ClientPackets.SYNCHRONIZE: #allows the client to request all the simulation data, like how it was when they joined the server.
                    server_switch_parameters_update_event.fire_initial(token_str)
                    server_button_parameters_update_event.fire_initial(token_str)
                    server_player_position_parameters_update_event.fire_initial(token_str)
                    server_rod_position_parameters_update_event.fire_initial(token_str)

                case packets.ClientPackets.CHAT:
                    client_chat_event.handle(packet_data, token_object.username)
    except websockets.exceptions.ConnectionClosed:
        log.info(f"User {token_object.username} disconnected")
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
    except Exception:
        log.error(traceback.format_exc())
        manager.disconnect(token_str)
        server_user_logout_event.fire(token_object.username)
