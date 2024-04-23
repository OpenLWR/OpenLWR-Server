from websockets.sync.server import serve
import config
from server import init_server

def main():
    with serve(init_server.init_server, config.server_ip, 7001) as server:
        server.serve_forever()

if __name__ == '__main__':
    main()
