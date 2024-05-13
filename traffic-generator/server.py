'''
import socket
import argparse

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                #print(f"Received data: {data}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URLLC Server")
    parser.add_argument('--host', type=str, default='172.16.0.2', help='Host IP')
    parser.add_argument('--port', type=int, default=12345, help='Port Number')
    args = parser.parse_args()
    
    start_server(args.host, args.port)
'''
import socket
import argparse

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        try:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    #print(f"Received data: {data}")
        except KeyboardInterrupt:
            print("Server shutdown requested by user.")
            s.close()
            # No need for explicit close here as 'with' context manager handles it

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URLLC Server")
    parser.add_argument('--host', type=str, default='172.16.0.2', help='Host IP')
    parser.add_argument('--port', type=int, default=12345, help='Port Number')
    args = parser.parse_args()
    
    start_server(args.host, args.port)
