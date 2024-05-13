import socket
import time
import os
import random
import argparse

def send_bursty_traffic(host, port, burst_size, min_interval, max_interval):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        try:
            while True:
                interval = random.uniform(min_interval, max_interval)
                time.sleep(interval)
                data = os.urandom(burst_size)
                s.sendall(data)
                print(f"Sent a burst of data for mmtc")
        except KeyboardInterrupt:
            print("Interrupted by user, closing connection.")
            s.close()  # Close the socket connection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MMTC Client")
    parser.add_argument('--host', type=str, default='172.16.0.2', help='Host IP')
    parser.add_argument('--port', type=int, default=12345, help='Port Number')
    parser.add_argument('--burst', type=int, default=375000, help='Burst Size in Bytes')
    parser.add_argument('--min-interval', type=float, default=0.5, help='Min Interval between bursts in seconds')
    parser.add_argument('--max-interval', type=float, default=2.0, help='Max Interval between bursts in seconds')
    args = parser.parse_args()

    send_bursty_traffic(args.host, args.port, args.burst, args.min_interval, args.max_interval)