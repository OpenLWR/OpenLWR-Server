import contextlib
import time
import threading
import asyncio
from websockets.sync.server import serve
import config

def main():
    from server import init_server
    with serve(init_server.init_server, config.server_ip, 7001) as server:
        server.serve_forever()

main()
import simulation

