import numpy as np
import zmq
import traceback


context = zmq.Context()
print("zmq context created") 

# socket to send control
socket_send_action = context.socket(zmq.PUB)
socket_send_action.bind("ipc:///tmp/socket_weights")
########################

# socket to receive metrics from RAN
socket_get_state = context.socket(zmq.SUB)
socket_get_state.setsockopt(zmq.CONFLATE, 1)
socket_get_state.connect("ipc:///tmp/socket_metrics")
socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")
########################

def get_metrics_multi():
    try:
        # Receive info from RAN (blocking)
        string_recv = socket_get_state.recv()
        print("Message received: \n", string_recv.decode())

        # Decode bytes to string and strip null terminator
        decoded_string = string_recv.decode().strip('\x00').strip()
        message_data = decoded_string.split()

        # Calculate number of UEs by assuming fixed parameters per UE
        numParamsPerUE = 5 + 3  # Adjust number based on known message structure
        numParams = 3
        totalParams = len(message_data) - 3  # Excludes last three entries which are not UE data
        num_ues = totalParams // numParamsPerUE
        #num_ues = int(len(message_data-3) / (numParams+3))

        # Dictionary to hold per UE data
        ue_data = {}

        # Parse data into a dictionary of dictionaries
        for i in range(num_ues):
            rnti = int(message_data[i * numParams])
            cqi = int(message_data[i * numParams + 1])
            backlog = int(message_data[i * numParams + 2])
            snr = float(message_data[num_ues*numParams+i*numParams+1])
            pending_data = float(message_data[num_ues*numParams+i*numParams+2])
            txb = float(message_data[num_ues*numParams+num_ues*numParams+i*2+1])

            ue_data[rnti] = {
                'CQI': cqi,
                'Backlog': backlog,
                'SNR': snr,
                'Pending Data': pending_data,
                'Tx' : txb
            }

        #print("Parsed UE data: ", ue_data)
        return ue_data

    except zmq.ZMQError as e:
        if e.errno == zmq.EAGAIN:
            pass  # No data to read
        else:
            traceback.print_exc()
            print("Error in receiving data")
    except Exception as ex:
        traceback.print_exc()
        print("An error occurred:", ex)

    return {}





if __name__ == "__main__":
    a = 999
    while True:
        a = a+1
        if (a==1000):
            c = np.random.randint(2, 7)
            d = np.random.randint(10, 17)
            a = 0
        ue_data = get_metrics_multi()
        print("Received from RAN: \n")
        print(ue_data)