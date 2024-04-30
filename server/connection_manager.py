import traceback

import websockets

class Token:
    def __init__(self, websocket, username, token):
        self.websocket = websocket
        self.username = username
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
            print("attempted to disconnect nonexistant client:",token)

    def send_user_packet(self, message: str, token: str):
        if len(message) > 1000:
            print(message)
        try:
            self.tokens[token].websocket.send(message)
        #TODO: this makes me fucking sad : ( fix
        #except websockets.exceptions.ConnectionClosedError:
        #    from server.server_events import server_user_logout_event
        #    username = self.username
        #    self.disconnect(self.token)
        #    print("client disconnected%s" % username)
        #    server_user_logout_event.fire(username)
        except Exception: # TODO: should we disconnect the client in this case?
            print(traceback.format_exc())

    def broadcast_packet(self, message: str):
        #TODO: this makes me fucking sad : ( fix
        #logout_tokens = []
        if len(message) > 1000:
            print(message)
        try:
            for token in self.tokens:
                try: 
                    self.tokens[token].websocket.send(message)
                except websockets.exceptions.ConnectionClosedError:
                    from server.server_events import server_user_logout_event
                    #queue the user to be logged out 
                    #TODO: this makes me fucking sad : ( fix
                    #username = self.tokens[token].username
                    #logout_tokens.append({"token" : token,"username" : username})
                except Exception: # TODO: should we disconnect the client in this case?
                    print(traceback.format_exc())
        except RuntimeError:
            print("[BUG] token array modified during loop over it")
            print(traceback.format_exc())
        #TODO: this makes me fucking sad : ( fix
        #for token in logout_tokens:
        #    self.disconnect(self.tokens[token]["token"])
        #for token in logout_tokens:
        #    print("client disconnected%s" % logout_tokens[token]["username"])
        #    server_user_logout_event.fire(username)

        

    def set_username(self, token: str, username: str):
        self.tokens[token].username = username

manager = ConnectionManager()
