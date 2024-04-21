import contextlib
import time
import threading
import asyncio
from websockets.sync.server import serve

def main():
    from server import init_server
    with serve(init_server.init_server, "0.0.0.0", 7001) as server:
        server.serve_forever()

main()
import simulation

