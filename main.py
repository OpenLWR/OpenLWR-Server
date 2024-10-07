from websockets.sync.server import serve
from websockets.http11 import Response
from websockets.datastructures import Headers
import config
from server import init_server
import threading
import json



def main():
    with serve(init_server.init_server, config.config["server_ip"], config.config["server_port"], process_request=process_request) as server:
        print(f"> Listening for clients on {config.config["server_ip"]}:{config.config["server_port"]}")
        server.serve_forever()

def process_request(connection, headers):
    path = connection.request.path
    print(path)
    if path == "/status":
        response = bytes(json.dumps({'status': '{}'.format(config.config["model"]), 'model': config.config["model"], 'motd': motd()}),'UTF-8')
        return Response(200, "OK", Headers({'Content-Type': 'application/json', 'Content-Length': len(response)}),
                        response)
    return None

def motd():
    return config.config["server_motd"]

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
        import log
        threading.Thread(target=import_simulation).start()
        main()
