from websockets.sync.server import serve
from websockets.http11 import Response
from websockets.datastructures import Headers
import config
from server import init_server
import threading
import json

def main():
    with serve(init_server.init_server, config.config["server_ip"], config.config["server_port"]) as server:
        print(f"> Listening for clients on {config.config["server_ip"]}:{config.config["server_port"]}")
        server.serve_forever()

def import_simulation():
    import simulation

if __name__ == '__main__':
    import logo
    print("> Welcome to OpenLWR-Server")
    import config
    if config.config != None:
        import log
        threading.Thread(target=import_simulation).start()
        main()