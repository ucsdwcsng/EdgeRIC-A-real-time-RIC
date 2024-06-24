#import hydra
import numpy as np
#import torch
import copy
import sys
import json
import zmq

# from neurwin_multi_threshold import NEURWIN
#from trainers.core.ppo import ppo_train
#from neurwin import NEURWIN
#from stream_rl.registry import ENVS
#from stream_rl.plots import visualize_neurwin_training, visualize_whittle_function, visualize_neurwin_ppo
import logging
import plotly.express as px
import plotly.graph_objs as go
import os
#from sanity_check import Environment
#from omegaconf import open_dict

log = logging.getLogger(__name__)

#from stream_rl.plots import visualize_neurwin_training, visualize_whittle_function, visualize_neurwin_ppo
#NUM_UES = 4
num_ues = 4

#agent = {}
#eplength = 5000
#algo = "neurwin"

context = zmq.Context()
print("zmq context created") 

socket_send_action = context.socket(zmq.PUB)
socket_send_action.bind("ipc:///tmp/socket_weights")

socket_send_action_site2 = context.socket(zmq.PUB)
socket_send_action_site2.bind("ipc:///tmp/socket_weights_site2")

socket_get_state = context.socket(zmq.SUB)
socket_get_state.setsockopt(zmq.CONFLATE, 1)
socket_get_state.connect("ipc:///tmp/socket_metrics")

socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")

socket_get_state_site2 = context.socket(zmq.SUB)
socket_get_state_site2.setsockopt(zmq.CONFLATE, 1)
socket_get_state_site2.connect("ipc:///tmp/socket_metrics_site2")

socket_get_state_site2.setsockopt_string(zmq.SUBSCRIBE, "")


ran_index = 0
curricid = 0
recvdricid = 0
f = 0
RNTIs = []
CQIs = []
BLs = []
txs = []
weight = np.zeros(num_ues*2+2)


queue_metrics = []
delay_metrics = 0
maxdelay_metrics = 0
delay_weights = 0
queue_weights = []
maxdelay_weights = 0

def get_metrics_multi():
    global recvdricid, curricid, ran_index, f, RNTIs, CQIs, BLs, txs, num_ues, queue_metrics, maxdelay_metrics, delay_metrics

    string = " "
    if(recvdricid>1):
        f=1
    
    curricid+=1
    numParams = 3
    try:
        # Every 1ms  - recieve info from RAN (blocking)
        string_recv = socket_get_state.recv()
        print(string_recv)
        messagedata= string_recv.split()
        print(f'received message length:', len(messagedata))
        if(len(messagedata)!= (num_ues*(numParams+2+numParams) + 3)):
            #print("I am here")
            return RNTIs, CQIs, BLs, txs
        recvdricid = int(messagedata[numParams*num_ues + numParams*num_ues + num_ues*2])
        print(f'received RIC ID and current RIC ID and f:', recvdricid, curricid, f)
            
        # while(curricid-recvdricid>1 and f==1):
        # #while(curricid-recvdricid>1):    
        #     #print(" I am here")
        #     string = socket_get_state.recv()
        #     messagedata= string.split()
        #     recvdricid = int(messagedata[numParams*num_ues + numParams*num_ues + num_ues*2])
        #     string_recv = string
        
        string_temp = string_recv
        string_temp = str(string_temp).replace(" ", ",\t")
        string_temp = str(string_temp).replace("b'", "")
        string_temp = str(string_temp).replace("\\x00'","")
        
        queue_metrics.append(string_recv)
        
        if(delay_metrics >= maxdelay_metrics ):
            string = queue_metrics.pop(0)
            #self.delay_metrics = 0
        else:
            delay_metrics = delay_metrics + 1

        messagedata= string.split() 
        
        RNTIs = np.zeros(num_ues)
        CQIs = np.zeros(num_ues)
        BLs = np.zeros(num_ues)
        txs = np.zeros(num_ues)
        MBs = np.zeros(num_ues)
        SNRs = np.zeros(num_ues)
        ul_data = np.zeros(num_ues)
       
            
        if len(messagedata) >= num_ues*numParams:
            
            
            msg_data_str = str(messagedata[numParams*num_ues+ numParams*num_ues + num_ues*2 +2])
            _frst = msg_data_str.find("'") + 1
            _last = msg_data_str.find("\\")
            msg_data_int = int(msg_data_str[_frst:_last])

            ran_index = msg_data_int

            for i in range(num_ues):
                RNTIs[i] = int(messagedata[i*numParams+0])
                CQIs[i] = int(messagedata[i*numParams+1])
                BLs[i] = int(messagedata[i*numParams+2]) 
                print("this rnti : " + str(RNTIs[i]) + "\n")
                # for j in range(num_ues):
                #     if int(messagedata[num_ues*numParams+j*2]) == RNTIs[i]:
                #         txs[i] = float(messagedata[num_ues*numParams+j*2+1])
                #         break 
            
        
    except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")    
        #print("RNTI, CQI, BL (get metrics func): " + str(RNTI) + str(CQI) + str(BL))
    return RNTIs, CQIs, BLs, txs

def send_weight(weights, flag):        

    global delay_weights, queue_weights, maxdelay_weights
    idx = 0
    #weights = [70, 0.5, 71, 0.5, 72, 0.0, 73, 0.0]
    str_to_send = ""
    while idx <len(weights):
        str_to_send = str_to_send + str(round(weights[idx],4)) + " "
        idx = idx +1
    #str_to_send = str_to_send+ "\n"

    str_to_send = str_to_send + str(curricid) + " " + str(ran_index) + " " + "\n"

    try:
        queue_weights.append(str_to_send)
        str_to_send_cur = ""

        if(delay_weights >= maxdelay_weights ):
            str_to_send_cur = queue_weights.pop(0)
            #if(flag == True): print("str_to_send_cur: ", str_to_send_cur)
            socket_send_action.send_string(str_to_send_cur)
            
            delay_weights = 0
        else:
            delay_weights = delay_weights + 1
        
    except zmq.ZMQError as e:
        if e.errno == zmq.EAGAIN:
            pass
        else:
            traceback.print_exec()
            print("blimey")
    

    if(flag == True): print("str_to_send_cur: ", str_to_send_cur)

if __name__ == "__main__":
    a = 999
    while True:
        a = a+1
        if (a==1000):
            c = np.random.randint(2, 7)
            d = np.random.randint(10, 17)
            a = 0
        RNTIs, CQIs, BLs, txs = get_metrics_multi()
        #print(" Received RNTIs are: " + str(RNTIs) + "\n")

        for i in range(len(RNTIs)):
            
            BL = BLs[i]
            CQI = CQIs[i]
            
            weight[i*2+1] = 0.2
            
            weight[i*2] = RNTIs[i]

           
            print("RNTI: " + str(RNTIs[i]) + " tx:" + str(txs[i]) + "\n")
               
        #weight[4] = 2 #c   weights[i] = numues*2 //c, weights[i] = numues*2 + 1 //d
        #weight[5] = 4 #d
        weight[8] = 2 #c
        weight[9] = 4 #d
        send_weight(weight, True) 