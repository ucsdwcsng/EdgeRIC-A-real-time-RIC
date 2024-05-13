'''
import socket
import time
import argparse

def send_periodic_traffic(host, port, packet_size, interval_ms):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            data = b'\x00' * packet_size  # Create a packet of the specified size (e.g., 6250 bytes)
            s.sendall(data)
            print(f"Sent {packet_size} bytes of data")
            time.sleep(interval_ms / 1000.0)  # Sleep for the specified interval in seconds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URLLC Client")
    parser.add_argument('--host', type=str, default='172.16.0.2', help='Host IP')
    parser.add_argument('--port', type=int, default=12345, help='Port Number')
    parser.add_argument('--packet-size', type=int, default=6250, help='Packet Size in Bytes')
    parser.add_argument('--interval-ms', type=float, default=10.0, help='Interval between packets in milliseconds')
    args = parser.parse_args()

    send_periodic_traffic(args.host, args.port, args.packet_size, args.interval_ms)
'''

import socket
import time
import argparse

def send_periodic_traffic(host, port, packet_size, interval_ms):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        try:
            while True:
                data = b'\x00' * packet_size  # Create a packet of the specified size
                s.sendall(data)
                print(f"Sent {packet_size} bytes of data for embb")
                time.sleep(interval_ms / 1000.0)  # Sleep for the specified interval in seconds
        except KeyboardInterrupt:
            print("Interrupted by user, closing connection.")
            s.close()  # Close the socket connection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URLLC Client")
    parser.add_argument('--host', type=str, default='172.16.0.2', help='Host IP')
    parser.add_argument('--port', type=int, default=12345, help='Port Number')
    # parser.add_argument('--packet-size', type=int, default=6250, help='Packet Size in Bytes')
    parser.add_argument('--packet-size', type=int, default=1000, help='Packet Size in Bytes')
    parser.add_argument('--interval-ms', type=float, default=12.0, help='Interval between packets in milliseconds')
    args = parser.parse_args()

    send_periodic_traffic(args.host, args.port, args.packet_size, args.interval_ms)
