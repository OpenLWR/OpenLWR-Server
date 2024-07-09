from websockets.sync.server import serve
from websockets.http11 import Response
from websockets.datastructures import Headers
import websockets #why are we doing websockets here?
import config
from server import init_server
import threading
import json


def main():
    with serve(init_server.init_server, config.server_ip, 7001, process_request=process_request) as server:
        print(f"> Listening for clients on {config.config["server_ip"]}:7001")
        server.serve_forever()

def process_request(connection, headers):
    path = connection.request.path
    print(path)
    if path == "/status":
        response = bytes(json.dumps({'status': '{}'.format(config.model), 'model': config.model, 'motd': motd()}),'UTF-8')
        return Response(200, "OK", Headers({'Content-Type': 'application/json', 'Content-Length': len(response)}),
                        response)
    return None

def motd():
    return """[p align=center][font_size=48]OpenLWR[/font_size]
version i have no fucking clue
running model {}[/p]""".format(config.model)

def import_simulation():
    import simulation

if __name__ == '__main__':
    print("""   ____                   __ _       ______ 
  / __ \\____  ___  ____  / /| |     / / __ \\
 / / / / __ \\/ _ \\/ __ \\/ / | | /| / / /_/ /
/ /_/ / /_/ /  __/ / / / /__| |/ |/ / _, _/ 
\\____/ .___/\\___/_/ /_/_____/__/|__/_/ |_|  
    /_/                                     \n""")
    print("> Welcome to OpenLWR-Server")
    import config
    if config.config != None:
        threading.Thread(target=import_simulation).start()
        main()
