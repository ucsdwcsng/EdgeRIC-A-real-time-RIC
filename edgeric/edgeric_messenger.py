import zmq
import time
import threading
import sys
import io
import metrics_pb2
import control_actions_pb2

# Set stdout encoding to UTF-8
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Global UE dictionary and ran_index variable
ue_dict = {}
ran_index = None
ric_index = None
correct = 0
incorrect = 0

context = zmq.Context()

# Create a publisher socket for SchedulingWeights
publisher_weights_socket = context.socket(zmq.PUB)
publisher_weights_socket.bind("ipc:///tmp/control_weights_actions")  # Bind to the IPC address for weights

# Create a publisher socket for Blanking
publisher_blanking_socket = context.socket(zmq.PUB)
publisher_blanking_socket.bind("ipc:///tmp/control_blanking_actions")  # Bind to the IPC address for blanking


# Create a subscriber socket to receive from RAN
subscriber_cqi_snr_socket = context.socket(zmq.SUB)
subscriber_cqi_snr_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages
subscriber_cqi_snr_socket.setsockopt(zmq.CONFLATE, 1)  # Set the socket to conflate mode
subscriber_cqi_snr_socket.connect("ipc:///tmp/socket_snr_cqi")  # Connect to the IPC address used by the C++ publisher for CQI and SNR

a = 0
b = 0
weights = []
global_sending_flag = False

def send_scheduling_weight(weights, flag):
    # Create an instance of the SchedulingWeights message
    msg = control_actions_pb2.SchedulingWeights()
    msg.ran_index = ran_index
    msg.weights.extend(weights)

    # Serialize the message to a string
    serialized_msg = msg.SerializeToString()

    # Send the serialized message over ZMQ
    publisher_weights_socket.send(serialized_msg)
    current_time = round(time.time(), 5)
    #print(f"Time: {current_time}s Sent to RAN: {msg} \n")

def send_blanking(ran_index, a, b):
    # Create an instance of the Blanking message
    msg = control_actions_pb2.Blanking()
    msg.ran_index = ran_index
    msg.a = a
    msg.b = b

    # Serialize the message to a string
    serialized_msg = msg.SerializeToString()

    # Send the serialized message over ZMQ
    publisher_blanking_socket.send(serialized_msg)
    current_time = round(time.time(), 5)
    #print(f"Time: {current_time}s Sent to RAN: {msg} \n")
    

def receive():
    global ran_index
    global ric_index
    message = subscriber_cqi_snr_socket.recv()
    metrics = metrics_pb2.Metrics()
    metrics.ParseFromString(message)
    ran_index = metrics.tti_cnt
    ric_index = metrics.ric_cnt
    #print(f"RAN Index: {ran_index}, RIC index: {ric_index} \n")
    return message

def get_metrics_multi():
    global ue_dict
    global ran_index
    global ric_index
    global global_sending_flag
    global correct, incorrect 
    message = receive()
    ue_dict = {}

    #message = subscriber_cqi_snr_socket.recv()
    #print(f"Received from EdgeRIC: {message}")

    metrics = metrics_pb2.Metrics()
    metrics.ParseFromString(message)
    ran_index = metrics.tti_cnt
    ric_index = metrics.ric_cnt
    if (ran_index-ric_index==1 or ran_index-ric_index==2): 
        correct=correct+1
        
    else: 
        incorrect = incorrect + 1
        # while (not (ran_index-ric_index==1 or ran_index-ric_index==2)):
        #     wts = [0] * (2 * 2)
        #     wts[0] = 70
        #     wts[1] = 0.5 
        #     wts[2] = 71
        #     wts[3] = 0.5
        #     f = 1
        #     send_scheduling_weight(wts, f)
        #     message = receive()
        #     metrics = metrics_pb2.Metrics()
        #     metrics.ParseFromString(message)
        #     ran_index = metrics.tti_cnt
        #     ric_index = metrics.ric_cnt

    for ue_metric in metrics.ue_metrics:
        rnti = ue_metric.rnti
        cqi = ue_metric.cqi
        backlog = ue_metric.backlog
        snr = ue_metric.snr
        pending_data = ue_metric.pending_data
        tx_bytes = ue_metric.tx_bytes
        rx_bytes = ue_metric.rx_bytes

        if rnti not in ue_dict:
            ue_dict[rnti] = {
                'CQI': None,
                'SNR': None,
                'Backlog': None,
                'Pending Data': None,
                'Tx_brate': None,
                'Rx_brate': None
            }

        ue_dict[rnti]['CQI'] = cqi
        ue_dict[rnti]['SNR'] = snr
        ue_dict[rnti]['Backlog'] = backlog
        ue_dict[rnti]['Tx_brate'] = tx_bytes
        ue_dict[rnti]['Rx_brate'] = rx_bytes
        ue_dict[rnti]['Pending Data'] = pending_data


    #print(f"RAN Index: {ran_index}, RIC index: {ric_index}, Correct count: {correct}, Incorrect count: {incorrect} \n")
    #print(f"UE Dictionary: {ue_dict} \n")
    ue_data = ue_dict
    return ue_data


