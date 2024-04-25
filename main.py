from websockets.sync.server import serve
import config
from server import init_server
import threading

def main():
    with serve(init_server.init_server, config.server_ip, 7001) as server:
        server.serve_forever()

def import_simulation():
    import simulation

if __name__ == '__main__':
    thread = threading.Thread(target=import_simulation)
    thread.start()
    main()
