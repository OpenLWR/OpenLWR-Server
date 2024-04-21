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
        token_to_remove = self.tokens.pop(token)
        del token_to_remove

    def send_user_packet(self, message: str, token: str):
        try:
            self.tokens[token].websocket.send(message)
        except:
            pass

    def broadcast_packet(self, message: str):
        for token in self.tokens:
            try: 
                self.tokens[token].websocket.send(message)
            except: # TODO: should we disconnect the client in this case?
                pass

manager = ConnectionManager()