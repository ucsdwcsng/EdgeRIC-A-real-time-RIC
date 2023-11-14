import itertools
import sys
import time
import random
import zmq


def main() -> None:
    if len(sys.argv) != 2:
        print('usage: publisher <bind-to>')
        #sys.exit(1)

   #bind_to = sys.argv[1]

    all_topics = [
        b'RIC.general',
        b'RIC.CQI',
        b'RIC.DL_Buffer',
        b'RIC.DL_throughput',
        b'RIC.PacketDelayBudget',
    ]

    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    s.bind("tcp://10.125.185.63:5000")

    print("Starting broadcast on topics:")
    print(f"   {all_topics}")
    print("Hit Ctrl-C to stop broadcasting.")
    print("Waiting so subscriber sockets can connect...")
    print("")
    time.sleep(1.0)

    msg_counter = itertools.count()
    try:
        for topic in itertools.cycle(all_topics):
            msg_body = str(random.randint(0,10))
            print(f"   Topic: {topic.decode('utf8')}, msg:{msg_body}")
            s.send_multipart([topic, msg_body.encode("utf8")])
            # short wait so we don't hog the cpu
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    print("Waiting for message queues to flush...")
    time.sleep(0.5)
    print("Done.")


if __name__ == "__main__":
    main()

 