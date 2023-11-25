import sys

import zmq
import time


def main():
    # topics = "RIC.CQI"
    # ctx = zmq.Context()
    # s = ctx.socket(zmq.SUB)
    # s.connect("tcp://10.125.185.63:5000")

    # # manage subscriptions
    # if not topics:
    #     print("Receiving messages on ALL topics...")
    #     s.setsockopt(zmq.SUBSCRIBE, b'')
    # else:
    #     print("Receiving messages on topics: %s ..." % topics)
         
    #     s.setsockopt(zmq.SUBSCRIBE, topics.encode('utf-8'))
    # print
    # try:
    #     while True:
    #         topic, msg = s.recv_multipart()
    #         print(
    #             '   Topic: {}, msg:{}'.format(
    #                 topic.decode('utf-8'), msg.decode('utf-8')
    #             )
    #         )
    # except KeyboardInterrupt:
    #     pass
    # print("Done.")
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind("tcp://*:12312")
    while True:
            sock.send_string("70 12313")
            sock.send_string("90 32123")
            time.sleep(0.01)


if __name__ == "__main__":
    main()