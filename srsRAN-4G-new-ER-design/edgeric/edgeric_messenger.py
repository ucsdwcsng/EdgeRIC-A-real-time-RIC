import zmq
import time
import threading
import sys
import io

# Set stdout encoding to UTF-8
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Global UE dictionary and ran_index variable
ue_dict = {}
ran_index = None

context = zmq.Context()

# Create a publisher socket
publisher_socket2 = context.socket(zmq.PUB)
publisher_socket2.bind("ipc:///tmp/control_actions")  # Bind to the IPC address

# Create a subscriber socket for CQI and SNR
subscriber_cqi_snr_socket = context.socket(zmq.SUB)
subscriber_cqi_snr_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages
subscriber_cqi_snr_socket.setsockopt(zmq.CONFLATE, 1)  # Set the socket to conflate mode
subscriber_cqi_snr_socket.connect("ipc:///tmp/socket_snr_cqi")  # Connect to the IPC address used by the C++ publisher for CQI and SNR

a = 0
b = 0
weights = []
global_sending_flag = False

def send_scheduling_weight(weights, flag): #publisher_dl_sched(weights):
    str_to_send = ""
    str_to_send = str_to_send + str(ran_index) + " "
    idx = 0
    global a, b
    while idx <len(weights):
        str_to_send = str_to_send + str(round(weights[idx],4)) + " "
        idx = idx +1
    str_to_send = str_to_send + str(a) + " " + str(b) + " "
    publisher_socket2.send_string(str_to_send)
    current_time = round(time.time(), 5)
    print(f"Time: {current_time}s Sent to RAN: {str_to_send} \n")    



def get_metrics_multi(): #subscriber_cqi_snr():
    global ue_dict  # Access the global UE dictionary
    global ran_index  # Access the global ran_index variable
    global global_sending_flag

    ue_dict.clear()

    message = subscriber_cqi_snr_socket.recv_string() # from mac.cc - this activates every TTI - rnti, snr, cqi, tx_brate, rx_brate, DL buffer
    print(f"Received from EdgeRIC: {message}")
    # Fetch pending data after processing CQI and SNR
    # pending_data = subscriber_pending_data() # from sched_time_pf.cc - rnti, UL buffer

    # Update ue_dict with pending data
    # for rnti, pd in pending_data.items():
    #     if rnti in ue_dict:
    #         ue_dict[rnti]['Pending Data'] = pd
    
    # Parse the message to update ue_dict and ran_index
    try:
    
        data = message.split()
        ran_index = int(data[0])  # First element is ran_index
        #ric_index = int(data[1])  # Second element is ric_index


        # while (global_sending_flag == False):
        #     message = subscriber_cqi_snr_socket.recv_string()
        #     data = message.split()
        #     ran_index = int(data[0])
        #     #message = subscriber_pending_data_socket.recv_string()

        #     if ran_index < 40000:
        #         print(f"Discarding message with ran_index: {ran_index}")
        #         global_sending_flag = False
                
        #     else:
        #         global_sending_flag = True

        for i in range(1, len(data), 7):
            rnti = int(data[i])
            cqi = int(data[i+1])
            backlog = int(data[i+2])
            tx_bits = float(data[i+3])
            rx_bits = float(data[i+4])
            pd = int(data[i+5])
            #snr = float(data[i+2])
            snr = float(data[i+6].replace('\x00', ''))  # Remove any null characters
            

            if rnti not in ue_dict:
                ue_dict[rnti] = {
                    'CQI': None,
                    'SNR': None,
                    'Backlog': None,
                    'Pending Data': None,
                    'Tx_brate' : None,
                    'Rx_brate' : None
                }

            ue_dict[rnti]['CQI'] = cqi
            ue_dict[rnti]['SNR'] = snr
            ue_dict[rnti]['Backlog'] = backlog
            ue_dict[rnti]['Tx_brate'] = tx_bits
            ue_dict[rnti]['Rx_brate'] = rx_bits
            ue_dict[rnti]['Pending Data'] = pd

       

    except ValueError as e:
        print(f"Error: {e}")
    
     # Update ue_dict with pending data
    # for rnti, pd in pending_data.items():
    #     if rnti in ue_dict:
    #         ue_dict[rnti]['Pending Data'] = pd

    # Print the current state of ue_dict and ran_index
    
    print(f"RAN Index: {ran_index} \n")
    print(f"UE Dictionary: {ue_dict} \n")
    ue_data = {}
    ue_data = ue_dict
    return ue_data

def main():
    
    while True: 
        ue_data = get_metrics_multi()
        global a, b, weights
        # compute some policy - call the policy with ue_dict
        a = 0
        b = 0
        weights.clear()
        # Initialize weights list with appropriate size (2 * number of UEs)
        weights = [0] * (2 * len(ue_dict))

        # Populate the weights list based on ue_dict
        i = 0
        for rnti in ue_dict.keys():
            if rnti == 73:
                weights[i*2] = rnti
                weights[i*2+1] = 0.9
            else:
                weights[i * 2] = rnti
                weights[i * 2 + 1] = 0.5
            i += 1
        

        # send the metrics
        # publisher_ul_blank()
        send_scheduling_weight(weights, True)

if __name__ == "__main__":
    main()
