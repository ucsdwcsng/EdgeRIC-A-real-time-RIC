
import zmq

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
ran_index = 0
curricid = 0
t = 0
num_mu_apps = 1
mu_app_ul_blank = False
mu_appl_dl_sched = True
string_to_send_weight = ""
string_to_send_ul_blanking = ""

def get_metrics_multi():
    global ran_index, curricid, string_to_send_ul_blanking, string_to_send_weight
    try:
        # Receive info from RAN (blocking)
        string_recv = socket_get_state.recv()
        #print("Message received: \n", string_recv.decode())

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
        msg_data_str = str(message_data[numParams*num_ues+ numParams*num_ues + num_ues*2 +2])
        _frst = msg_data_str.find("'") + 1
        _last = msg_data_str.find("\\")
        msg_data_int = int(msg_data_str[_frst:_last])

        ran_index = msg_data_int
        #print("Parsed UE data: ", ue_data)
        if (mu_app_ul_blank==False):
            string_to_send_ul_blanking = str(0) + " " + str(0) + " "
        if (mu_appl_dl_sched==False):
            numues = len(ue_data)
            for i in range(numues):
                # Store RNTI and corresponding weight
                weights[i*2+0] = RNTIs[i]
                weights[i*2+1] = 1/numues
            string_to_send_weight = ""
            while idx <len(weights):
                string_to_send_weight = string_to_send_weight + str(round(weights[idx],4)) + " "
                idx = idx +1
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

def send_scheduling_weight(weights, flag):   
    global t, string_to_send_weight, num_mu_apps
    
    idx = 0
    #weights = [70, 0.5, 71, 0.5, 72, 0.0, 73, 0.0]
    string_to_send_weight = ""
    while idx <len(weights):
        string_to_send_weight = string_to_send_weight + str(round(weights[idx],4)) + " "
        idx = idx +1
    t = t+1
    if(flag == True): print("Downlink action: Per UE weights: ", string_to_send_weight)
    if (t==num_mu_apps):
        send_control()

def send_ul_prb(a,b,flag):
    global t, string_to_send_ul_blanking, num_mu_apps
    string_to_send_ul_blanking = str(a) + " " + str(b) + " " 
    t = t+1
    if(flag == True): print("Uplink action: PRBs to blank: ", string_to_send_ul_blanking)
    if (t==num_mu_apps):
        send_control()

    

def send_control():
    global ran_index, curricid, string_to_send_weight, string_to_send_ul_blanking, t
    a = 0
    b = 0
    try:
        curricid += 1
        str_to_send = string_to_send_weight + string_to_send_ul_blanking + str(curricid) + " " + str(ran_index) + " " + "\n"
        socket_send_action.send_string(str_to_send)
        t = 0
    except zmq.ZMQError as e:
        if e.errno == zmq.EAGAIN:
            pass  # Handle retry or log as needed
        else:
            traceback.print_exc()
            print("Error in ZMQ operation")

    print("str_to_send_RAN: ", str_to_send)
    