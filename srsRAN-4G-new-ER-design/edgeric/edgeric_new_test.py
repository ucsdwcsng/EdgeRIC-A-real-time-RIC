import zmq
import time
import threading

# Global UE dictionary
ue_dict = {}

def publisher_thread(context):
    # Create a publisher socket
    publisher = context.socket(zmq.PUB)
    publisher.bind("ipc:///tmp/socket_blanking")  # Bind to the IPC address

    while True:
        a = 10  # Example value for a
        b = 17  # Example value for b

        # Create the message by concatenating the integers as strings
        message = f"{a} {b}"
        publisher.send_string(message)

        print(f"Sent: {message}")

        time.sleep(0.001)  # Wait for 1 millisecond before sending the next message

def subscriber_thread(context):
    global ue_dict  # Access the global UE dictionary

    # Create a subscriber socket
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("ipc:///tmp/socket_ul_pending_data")  # Connect to the IPC address used by the C++ publisher
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

    while True:
        message = subscriber.recv_string()
        print(f"Received: {message}")

        # Parse the message to update ue_dict
        try:
            data = list(map(int, message.split()))
            if len(data) % 2 != 0:
                raise ValueError("Received invalid message format")
            
            for i in range(0, len(data), 2):
                rnti = data[i]
                pending_data = data[i+1]
                ue_dict[rnti] = pending_data

        except ValueError as e:
            print(f"Error: {e}")

        # Print the current state of ue_dict
        print(f"UE Dictionary: {ue_dict}")

def main():
    context = zmq.Context()

    # Start the publisher thread
    pub_thread = threading.Thread(target=publisher_thread, args=(context,))
    pub_thread.start()

    # Start the subscriber thread
    sub_thread = threading.Thread(target=subscriber_thread, args=(context,))
    sub_thread.start()

    # Keep the main thread alive
    pub_thread.join()
    sub_thread.join()

if __name__ == "__main__":
    main()
