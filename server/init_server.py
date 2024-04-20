from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from server.connection_manager import manager
from server.server_events import user_logout_event

def init_server(app):
    @app.websocket("/ws/{token}")
    async def websocket_endpoint(websocket: WebSocket, token: str):
        await manager.connect(websocket, token)
        token_object = manager.get_token_from_str(token)
        try:
            while True:
                data = await websocket.receive_text()
                print(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, token)
            await user_logout_event.fire(token_object.username)

def init_fastapi():
    app = FastAPI()
    
    init_server(app)

    return app

app = init_fastapi()