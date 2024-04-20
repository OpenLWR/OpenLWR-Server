from fastapi import WebSocket

class Token:
    def __init__(self, websocket, username, token):
        self.websocket = websocket
        self.username = username
        self.token = token

class ConnectionManager:
    def __init__(self):
        self.tokens = {}

    async def connect(self, websocket: WebSocket, token: str):
        await websocket.accept()
        self.tokens[token] = Token(websocket, "jeff (TODO)", token)

    def disconnect(self, websocket: WebSocket, token: str):
        token_to_remove = self.tokens.pop(token)
        del token_to_remove

    async def send_user_packet(self, message: str, token):
        await self.tokens[token].websocket.send_text(message)

    async def broadcast_packet(self, message: str):
        for token in self.tokens:
            await self.tokens[token].websocket.send_text(message)

    def get_token_from_str(self, string):
        return self.tokens[string]

manager = ConnectionManager()