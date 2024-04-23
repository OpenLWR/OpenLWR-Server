import traceback


class Token:
    def __init__(self, websocket, username, token):
        self.websocket = websocket
        self.username = username
        self.token = token

class ConnectionManager:
    def __init__(self):
        self.tokens = {}

    def connect(self, websocket, token: str):
        self.tokens[token] = Token(websocket, "jeff (TODO)", token)
        return self.tokens[token]

    def disconnect(self, token: str):
        if token in self.tokens:
            self.tokens.pop(token)
        else:
            print("attempted to disconnect nonexistant client:",token)

    def send_user_packet(self, message: str, token: str):
        try:
            self.tokens[token].websocket.send(message)
        except Exception:
            print(traceback.format_exc())

    def broadcast_packet(self, message: str):
        for token in self.tokens:
            try: 
                self.tokens[token].websocket.send(message)
            except Exception: # TODO: should we disconnect the client in this case?
                print(traceback.format_exc())

manager = ConnectionManager()
