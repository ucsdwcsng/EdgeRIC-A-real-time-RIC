import zmq


def get_state(socket):
    '''
    Gets state by pulling info off some socket
    Returns rnti of the last cqi received

    socket - zmq sub socket subscribed to state
    '''
    message = socket.recv()
    message = message.split()
    print("rnti:" + str(int(message[0])) + ", cqi: " + str((int(message[1]))))
    return int(message[0])


def step(socket, rnti):
    '''
    Sends some random weight to the ran
    
    socket - zmq pub socket going to state
    rnti - id of some ue
    '''
    message = str(rnti) + " " + str("1")
    socket.send_string(message)


context = zmq.Context()
socket_send_action = context.socket(zmq.PUB)
socket_get_state = context.socket(zmq.SUB)

socket_send_action.connect("ipc:///tmp/socket_weights")
socket_get_state.connect("ipc:///tmp/socket_metrics")

socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    ue_id = get_state(socket_get_state)
    step(socket_send_action, ue_id)
