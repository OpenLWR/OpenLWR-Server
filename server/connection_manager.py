import traceback
import websockets
import log

class Token:
    def __init__(self, websocket, username, token):
        self.websocket = websocket
        self.username = username
        self.position = {"x":0,"y":0,"z":0} #TODO: Move somewhere else?
        self.token = token

class ConnectionManager:
    def __init__(self):
        self.tokens = {}

    def connect(self, websocket, token: str):
        self.tokens[token] = Token(websocket, "No Username", token)
        return self.tokens[token]

    def disconnect(self, token: str):
        if token in self.tokens:
            self.tokens.pop(token)
        else:
            log.warning(f"attempted to disconnect nonexistent client: {token}")

    def send_user_packet(self, message: str, token: str):
        try:
            self.tokens[token].websocket.send(message)
        except Exception:
            log.error(traceback.format_exc())

    def broadcast_packet(self, message: str):
        try:
            token_list = self.tokens.copy() #prevents "dictionary changed size during iteration" error
            for token in token_list:
                try: 
                    self.tokens[token].websocket.send(message)
                except websockets.exceptions.ConnectionClosedError:
                    from server.server_events import server_user_logout_event
                except Exception:
                    log.error(traceback.format_exc())
        except RuntimeError:
            log.error(traceback.format_exc())

        

    def set_username(self, token: str, username: str):
        self.tokens[token].username = username

manager = ConnectionManager()
