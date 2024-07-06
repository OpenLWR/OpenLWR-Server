from websockets.sync.server import serve

from server import init_server
import threading


def main():
    with serve(init_server.init_server, config.config["server_ip"], 7001) as server:
        print(f"> Listening for clients on {config.config["server_ip"]}:7001")
        server.serve_forever()

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
