import zmq
import time
ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock.bind("ipc:///tmp/socket_metrics")
while True:
            sock.send_string("70 0 90 0")
            # sock.send_string("90 0")
            # print("sending")
            time.sleep(0.001)