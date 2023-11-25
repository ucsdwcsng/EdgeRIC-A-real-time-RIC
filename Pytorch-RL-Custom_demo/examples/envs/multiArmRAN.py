'''
Environment to calculate the Whittle index values as a deep reinforcement 
learning environment modelled after the OpenAi Gym API.
Same mini-batch episodes have the same trajectory values for comparing their returns.
This is the down-link environment.
'''

from collections import defaultdict
from email.policy import default
from pickletools import long1
from typing import DefaultDict
import gym
import math
import sys

import zmq

import time
import random
import datetime
import numpy as np
import pandas as pd
from gym import spaces

import json


class multiArmRAN(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize, episodeLimit, fixedSizeMDP, noiseVar, cost=0, zmq_params=None, numArms= 2):

        super(multiArmRAN, self).__init__()
        self.cost = cost
        self.numArms =numArms
        self.numParams = 4   # RNTI, CQI, Backlog, Media buffer
        self.scheduleArms =1
        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0
        self.currentEpisode = 0
        self.noiseVar = noiseVar

        self.rate = r1
        self.maxBufferSize = maxBufferSize  # 500
        self.high_RB = high_RB  # Dummy
        self.low_RB = low_RB  # Dummy
        self.arm = {0:  np.zeros(self.numArms*self.numParams, dtype=np.double)} 

        self.train = Training
        self.batchSize = batchSize
        self.miniBatchCounter = 0
        self.episodeLimit = episodeLimit
        self.fixedSizeMDP = fixedSizeMDP
         #zmq inits
        # for pubbing action
        self.context = zmq.Context()
        print("zmq context created")

        self.socket_send_action = self.context.socket(zmq.PUB)
        self.socket_send_action.bind("ipc:///tmp/socket_weights")

        # for subbing state
        self.socket_get_state = self.context.socket(zmq.SUB)
        self.socket_get_state.connect("ipc:///tmp/socket_metrics")
        self.socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")

        self.socket_mbuff = self.context.socket(zmq.SUB)
        self.socket_mbuff.connect("ipc:///tmp/socket_mbuff_1")
        self.socket_mbuff.setsockopt_string(zmq.SUBSCRIBE, "")

        self.socket_mbuff_1 = self.context.socket(zmq.SUB)
        self.socket_mbuff_1.connect("ipc:///tmp/socket_mbuff_2")
        self.socket_mbuff_1.setsockopt_string(zmq.SUBSCRIBE, "")

        
        self.socket_reset = self.context.socket(zmq.PUB)
        self.socket_reset.bind("ipc:///tmp/socket_reset")
        
        self.socket_tti = self.context.socket(zmq.PUB)
        self.socket_tti.bind("ipc:///tmp/socket_tti")


        self.socket_logging = self.context.socket(zmq.PUB)
        self.socket_logging.bind("ipc:///tmp/socket_logging_seq_ric")

        f_params = open("params_edgeric.txt")
        line_delay = 1
        idx_delay_metrics = 0
        idx_delay_weights = 1
        lines = f_params.readlines()
        max_delay_metrics = int(lines[line_delay].split()[idx_delay_metrics])
        max_delay_weights = int(lines[line_delay].split()[idx_delay_weights])
        f_params.close()

        print("\n","max_delay_metrics: ", max_delay_metrics,"max_delay_weights: ", max_delay_weights, "\n" )

        self.queue_metrics = []
        self.queue_mbuff = []
        self.queue_mbuff_1 = []
        self.delay_metrics = 0
        self.maxdelay_metrics = max_delay_metrics
        self.delay_mbuff = 0
        self.queue_weights = []
        self.delay_weights = 0
        self.maxdelay_weights = max_delay_weights
        self.high_weight = 0.9
        self.low_weight = 0.1
        
        self.index_weight = 0

        
        self.fileout_period = 60 # 10 sec
        self.time_init = time.time()

        self.prev_metrics_index = 0
        self.cur_metrics_index = 0
        self.returned_weight_index = 0
        self.cur_metrics_sending_time = 0
        self.overdt_cnt = 0
        self.metrics_index_delay_cnt = 0
        self.weight_index_delay_cnt = 0

        self.cnt_notValid = 0
        
        self.dt = 0
        self.dt_cnt = 0
        self.MAX_INDEX = 10240
        

        ## get some rnti
        self.observationSize = self.numArms*(self.numParams-1)
        
        lowState = np.zeros(self.observationSize, dtype=np.double)
        highState = lowState
        for i in range(self.numArms): 
            highState[i] = self.maxBufferSize
            highState[i*2+1] = 300000
            highState[i*2+2] = 15

        
        self.action_space = spaces.Discrete(9)
        
        self.observation_space = spaces.Box(
            lowState, highState, dtype=np.double)


    
    def _calReward(self, curState, nextState):
        ''' function to calculate next state, and reward given the action'''
        
        total_reward = 0        
        
        
        tx_bytes_total = (nextState[0]) + (nextState[3])
        MB_total = (nextState[1] + nextState[4])

        total_reward = tx_bytes_total/(2*10000) ; 
        
        
        
        return total_reward

    

    def step_weights(self, weights):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        
        curState = np.array([self.arm[0][2], self.arm[0][3] , self.arm[0][1] , self.arm[0][6], self.arm[0][7], self.arm[0][5]], dtype=np.double)
        
        self.episodeTime += 1
        
        #PUB action
        isValid = False

        
        RNTI1 =self.arm[0][0] 
        RNTI2 =self.arm[0][4] 

        weights_rntis = [int(RNTI1), weights[0], int(RNTI2), weights[1]]

        idx = 0
        str_to_send = ""
        while idx <len(weights_rntis):
            str_to_send = str_to_send + str(round(weights_rntis[idx],2)) + " "
            idx = idx +1
        
        
        
        self.send_weight(weights,False)
        
        

        done = self.episodeTime == self.episodeLimit

        
        # get next state
        isValid = False

        while not isValid :

            nextState, action, curState, isValid = self.get_state_SdashAS() 

        
        
        self.arm[0][0] = RNTI1
        self.arm[0][1] = nextState[2]
        self.arm[0][2] = nextState[0]
        self.arm[0][3] = nextState[1]

        self.arm[0][4] = RNTI2
        self.arm[0][5] = nextState[5]
        self.arm[0][6] = nextState[3]
        self.arm[0][7] = nextState[4]
        
        reward = self._calReward(curState, nextState )


        info = {}
        done = False
        return nextState, reward, done, info

    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)

        curState = np.array([self.arm[0][2], self.arm[0][3] , self.arm[0][1] , self.arm[0][6], self.arm[0][7], self.arm[0][5]], dtype=np.double)
        
        
        self.episodeTime += 1
       

        #PUB action
        isValid = False

        
        self.send_action(action)
        

        done = self.episodeTime == self.episodeLimit

        
        # get next state
        RNTI1, CQI1, BL1, MB1, RNTI2, CQI2, BL2, MB2 = self.get_state() # to make 

        
        
        self.arm[0][0] = RNTI1
        self.arm[0][1] = CQI1
        self.arm[0][2] = BL1
        self.arm[0][3] = MB1

        self.arm[0][4] = RNTI2
        self.arm[0][5] = CQI2
        self.arm[0][6] = BL2
        self.arm[0][7] = MB2
        
        nextState = np.array([BL1, MB1, CQI1, BL2, MB2, CQI2], dtype=np.double)
        
        reward = self._calReward(curState, nextState )


        info = {}
        done = False
        return nextState, reward, done, info


    def step_SdashAS(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)
        
        self.episodeTime += 1
        

        #PUB action
        isValid = False

        while not isValid :

            elf.send_action(action)
            

            done = self.episodeTime == self.episodeLimit

            
            
            nextState, action, curState, isValid = self.get_state_SdashAS()

            
        
        reward = self._calReward(action, curState, nextState )


        info = {}
        done = False
        return curState, nextState, reward, done, info

    def get_state_app(self):
        #ZMQ sub
        
        mbuff_message = ""
        mbuff_message_1 = ""

                  
        MB_x = self.arm[0][3]
        
        MB_y = self.arm[0][7]
        mbuff_message_temp = ""
        mbuff_message_1_temp = ""
        
        
        try: 
            mbuff_message_temp = self.socket_mbuff.recv(flags=zmq.NOBLOCK)  # receive a media buffer state from ue1
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")

        try: 
            mbuff_message_1_temp = self.socket_mbuff_1.recv(flags=zmq.NOBLOCK)  # receive a media buffer state from ue1
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        self.queue_mbuff.append(mbuff_message_temp)
        self.queue_mbuff_1.append(mbuff_message_1_temp)
        
        if(self.delay_mbuff >= self.maxdelay_metrics ):
            mbuff_message = self.queue_mbuff.pop(0)
            mbuff_message_1 = self.queue_mbuff_1.pop(0)
            
        else:
            self.delay_mbuff = self.delay_mbuff + 1

        if len(mbuff_message) > 0:
            MB_x = int(mbuff_message)
            self.arm[0][3] = MB_x

        if len(mbuff_message_1) > 0 :
            MB_y = int(mbuff_message_1)
            self.arm[0][7] = MB_y
        
        return MB_x, MB_y





    def get_state(self):
        #ZMQ sub
        string = ""
        mbuff_message = ""
        mbuff_message_1 = ""

        RNTI_x = self.arm[0][0]            
        CQI_x = self.arm[0][1]
        BL_x = self.arm[0][2]            
        MB_x = self.arm[0][3]
        RNTI_y = self.arm[0][4]
        CQI_y = self.arm[0][5]
        BL_y = self.arm[0][6] 
        MB_y = self.arm[0][7]
        mbuff_message_temp = "0"
        mbuff_message_1_temp = "0"
        
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            flag_recved = False
            while(flag_recved is not True):
                string_temp = self.socket_get_state.recv()
               
                self.queue_metrics.append(string_temp)
                
                if(self.delay_metrics >= self.maxdelay_metrics ):
                    string = self.queue_metrics.pop(0)
                    
                    
                else:
                    self.delay_metrics = self.delay_metrics + 1

                messagedata= string.split() 
                
                if len(messagedata) >= 23 :
                    
                    try:
                        idx = 0
                        RNTI_x = int(messagedata[idx]) ; idx +=1
                        if int(messagedata[idx]) > 0 : CQI_x =  int(messagedata[idx]); idx +=1 
                        BL_x = int(messagedata[idx]) ; idx +=1
                        THRPT_x = int(messagedata[idx]); idx +=1
                        
                        RNTI_y = int(messagedata[idx]) ; idx +=1
                        if int(messagedata[idx]) > 0 : CQI_y =  int(messagedata[idx]) ; idx +=1
                        BL_y = int(messagedata[idx]) ; idx +=1
                        THRPT_y = int(messagedata[idx]); idx +=1
			
                        prev_weight_x = float(messagedata[idx]) ; idx +=1
                        prev_weight_y = float(messagedata[idx]) ; idx +=1
                        self.returned_weight_index = int(messagedata[idx]) ; idx +=1
                        self.prev_metrics_index = self.cur_metrics_index
                        self.cur_metrics_index = int(messagedata[idx]) ; idx +=1
                        self.cur_metrics_sending_time = float(messagedata[idx]) ; idx +=1
                        cur_time = time.time()
                        dt = cur_time-  self.cur_metrics_sending_time
                        
                        if dt > 0.001:
                            self.overdt_cnt = self.overdt_cnt + 1
                        
                        
                       
                        if self.cur_metrics_index < self.prev_metrics_index: 
                            self.prev_metrics_index = self.prev_metrics_index - self.MAX_INDEX

                        if self.cur_metrics_index - self.prev_metrics_index > 1:
                            self.metrics_index_delay_cnt = self.metrics_index_delay_cnt + 1
                        
                        index_weight_temp = self.index_weight
                        if self.index_weight < self.returned_weight_index:
                            index_weight_temp = self.returned_weight_index - self.MAX_INDEX
                        
                        if index_weight_temp - self.returned_weight_index > 1:
                            self.weight_index_delay_cnt = self.weight_index_delay_cnt + 1
                            
                
                        # update global variables
                        self.arm[0][0] = RNTI_x 
                        self.arm[0][1] = CQI_x 
                        self.arm[0][2] = BL_x            
                        
                        self.arm[0][4] = RNTI_y
                        self.arm[0][5] = CQI_y
                        self.arm[0][6] = BL_y 

                    except ValueError:
                        print ('Invalid number')
                    
                

                flag_recved = True
                self.index_weight = self.cur_metrics_index

                # 2. RIC received state information from RAN
                seq_2 = str(time.time()) + ",\t" + "2"  + ",\t" + str(self.cur_metrics_index)  + ",\t" + str(self.index_weight) + "\n"
                
            
        except zmq.ZMQError as e:
            #print("none")
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
          

        return RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y
        
       
    
    
    def get_state_SdashAS(self):

        curState = np.array([0, 0, 0, 0, 0, 0], dtype=np.double)
        nextState = np.array([0, 0, 0, 0, 0, 0], dtype=np.double)
        action = -1
        isValid = False
        

        #ZMQ sub
        string = ""
        mbuff_message = ""
        mbuff_message_1 = ""

        RNTI_x = self.arm[0][0]            
        CQI_x = self.arm[0][1]
        BL_x = self.arm[0][2]            
        MB_x = self.arm[0][3]
        RNTI_y = self.arm[0][4]
        CQI_y = self.arm[0][5]
        BL_y = self.arm[0][6] 
        MB_y = self.arm[0][7]


        RNTI_x_next = self.arm[0][0]            
        CQI_x_next = self.arm[0][1]
        BL_x_next = self.arm[0][2]            
        MB_x_next = self.arm[0][3]
        RNTI_y_next = self.arm[0][4]
        CQI_y_next = self.arm[0][5]
        BL_y_next = self.arm[0][6] 
        MB_y_next = self.arm[0][7]

        Weight_x_a = 0 
        Weight_y_a  = 0 

        mbuff_message_temp = "0"
        mbuff_message_1_temp = "0"
        
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            flag_recved = False
            while(flag_recved is not True):
                
                string_temp = self.socket_get_state.recv()
                self.queue_metrics.append(string_temp)
                self.queue_mbuff.append(mbuff_message_temp)
                self.queue_mbuff_1.append(mbuff_message_1_temp)
                
                if(self.delay_metrics >= self.maxdelay_metrics ):
                    string = self.queue_metrics.pop(0)
                    mbuff_message = self.queue_mbuff.pop(0)
                    mbuff_message_1 = self.queue_mbuff_1.pop(0)
                    
                else:
                    self.delay_metrics = self.delay_metrics + 1

                messagedata= string.split() 
               
                


                if len(messagedata) >=24:
                    

                    # 0 - 10: nextState
                    RNTI_x_next = int(messagedata[0])
                    if int(messagedata[1]) > 0 : CQI_x_next =  int(messagedata[1]) 
                    BL_x_next = int(messagedata[2])
                    RNTI_y_next = int(messagedata[3])
                    if int(messagedata[4]) > 0 : CQI_y_next =  int(messagedata[4]) 
                    BL_y_next = int(messagedata[5])

                    prev_weight_x_next = float(messagedata[6])
                    prev_weight_y_next = float(messagedata[7])
                    self.returned_weight_index = int(messagedata[8])
                    self.prev_metrics_index = self.cur_metrics_index
                    self.cur_metrics_index = int(messagedata[9])
                    self.cur_metrics_sending_time = float(messagedata[10])

                    ## 11 ~ 17: Action
                    RNTI_x_a = int (float(messagedata[11]))
                    Weight_x_a = float (messagedata[12])
                    RNTI_y_a = int (float(messagedata[13]))
                    Weight_y_a = float (messagedata[14])
                    weight_index_a = int (messagedata[15])
                    metrics_index_a = int (messagedata[16])
                    weight_sending_time = float(messagedata[17])

                    # 18 - 28: curState

                    RNTI_x = int(messagedata[18])
                    if int(messagedata[19]) > 0 : CQI_x =  int(messagedata[19]) 
                    BL_x = int(messagedata[20])
                    RNTI_y = int(messagedata[21])
                    if int(messagedata[22]) > 0 : CQI_y =  int(messagedata[22]) 
                    BL_y = int(messagedata[23])

                    prev_weight_x = float(messagedata[24])
                    prev_weight_y = float(messagedata[25])
                    returned_prev_weight_index = int(messagedata[26])
                    returned_prev_metrics_index = int(messagedata[27])
                    returned_prev_metrics_sending_time = float(messagedata[28])

                    ## check the validation
                    reason = 0
                    
                    if self.returned_weight_index == weight_index_a and weight_index_a -1 <= returned_prev_weight_index :
                        reason = 1
                        if self.cur_metrics_index == metrics_index_a + 2 and self.cur_metrics_index == returned_prev_metrics_index +1 :
                            reason = 2
                            if self.cur_metrics_sending_time > returned_prev_metrics_sending_time > weight_sending_time: 
                            
                                isValid = True
            
                                print("valid: ",self.cnt_notValid )

                    if (weight_index_a <=1 ): 
                        isValid = True


                    if isValid is False:
                        self.cnt_notValid = self.cnt_notValid +1
                        print("not valid: ",self.cnt_notValid, reason )


                    print('valid: ',isValid )

                    cur_time = time.time()
                    dt = cur_time-  self.cur_metrics_sending_time
                    

                    if dt > 0.001:
                        self.overdt_cnt = self.overdt_cnt + 1
                        print("\n",cur_time, "dt", dt, "cnt:", self.overdt_cnt, "sending_time at RAN:",self.cur_metrics_sending_time, "\n")

                    if self.cur_metrics_index - self.prev_metrics_index > 1:
                        self.metrics_index_delay_cnt = self.metrics_index_delay_cnt + 1
                        print("\n",cur_time, "metrics_index_delay", self.cur_metrics_index - self.prev_metrics_index, "cnt:", self.metrics_index_delay_cnt,"\n",)

                    if self.index_weight- self.returned_weight_index > 1:
                        self.weight_index_delay_cnt = self.weight_index_delay_cnt + 1
                        print("\n",cur_time, "weight_index_delay", self.index_weight - self.returned_weight_index, "cnt:", self.weight_index_delay_cnt,"\n",)
  
                
                if len(mbuff_message) > 0:
                    MB_x = int(mbuff_message)
                else:
                    MB_x = self.maxBufferSize


                if len(mbuff_message_1) > 0 :
                    MB_y = int(mbuff_message_1)
                else:
                    MB_y = self.maxBufferSize

                print(self.returned_weight_index,self.index_weight )
                if (self.returned_weight_index == self.index_weight-1 ): 
                    flag_recved = True
                    print("true")
                

                if (self.returned_weight_index ==0):
                    flag_recved = True
                
                if len(messagedata) >=24 and self.returned_weight_index == 0:
                    flag_recved = True
                    isValid = True

           
            
        except zmq.ZMQError as e:
            #print("none")
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        
        MB_x_next = self.maxBufferSize 
        MB_y_next = self.maxBufferSize 

        curState = np.array([BL_x, MB_x, CQI_x, BL_y, MB_y, CQI_y], dtype=np.double)
        nextState = np.array([BL_x_next, MB_x_next, CQI_x_next, BL_y_next, MB_y_next, CQI_y_next], dtype=np.double)
        
        if Weight_x_a == 0.9:
            action = 0                        
        elif Weight_x_a == 0.8:
            action = 1
        elif Weight_x_a == 0.7:
            action = 1
        elif Weight_x_a == 0.6:
            action = 1
        elif Weight_x_a == 0.5:
            action = 4
        elif Weight_x_a == 0.4:
            action = 5
        elif Weight_x_a == 0.3:
            action = 6
        elif Weight_x_a == 0.2:
            action = 7
        elif Weight_x_a == 0.1:
            action = 8
        
        print('action', action)



        return nextState, action, curState, isValid 
    
    
    def send_action(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        
        self.episodeTime += 1

        #PUB action
        if action == 0:
            weight1 = 0.9
            weight2 = 0.1
        elif action == 1:    
            weight1 = 0.8
            weight2 = 0.2
        elif action == 2:    
            weight1 = 0.7
            weight2 = 0.3
        elif action == 3:    
            weight1 = 0.6
            weight2 = 0.4
        elif action == 4:    
            weight1 = 0.5
            weight2 = 0.5
        elif action == 5:    
            weight1 = 0.4
            weight2 = 0.6
        elif action == 6:    
            weight1 = 0.3
            weight2 = 0.7
        elif action == 7:    
            weight1 = 0.2
            weight2 = 0.8
        else:    
            weight1 = 0.1
            weight2 = 0.9
            

        RNTI1 =self.arm[0][0] 
        RNTI2 =self.arm[0][4] 

        weights = [int(RNTI1), weight1, int(RNTI2), weight2]
        

        idx = 0
        str_to_send = ""
        while idx <len(weights):
            str_to_send = str_to_send + str(round(weights[idx],2)) + " "
            idx = idx +1
        
        self.send_weight(weights,False)
        
        


        
    ###### Added for weight-based scheduling by whko  ####
    def dummy(self):
        ''' Standard Gym function for supplying initial episode state.'''
        print("testing")
        

    def get_metrics(self):
        #ZMQ sub
        string = ""
        try:
            # Every 1ms  - recieve info from RAN (blocking)
            string_temp = self.socket_get_state.recv()

            

            self.queue_metrics.append(string_temp)
            
            if(self.delay_metrics >= self.maxdelay_metrics ):
                string = self.queue_metrics.pop(0)
            else:
                self.delay_metrics = self.delay_metrics + 1



            messagedata= string.split() 
            
            
            RNTI_x = self.arm[0][0]            
            CQI_x = self.arm[0][1]
            BL_x = self.arm[0][2]            
            RNTI_y = self.arm[0][3]
            CQI_y = self.arm[0][4]
            BL_y = self.arm[0][5]
            
            
            if len(messagedata) >= 6:
                
                RNTI_x = int(messagedata[0])
                CQI_x = int(messagedata[1])
                BL_x = int(messagedata[2])
                
                RNTI_y = int(messagedata[3])
                CQI_y = int(messagedata[4])
                BL_y = int(messagedata[5])
                
                
                    
                self.arm[0][0] = RNTI_x
                if CQI_x > 0 : self.arm[0][1]= CQI_x
                else:  CQI_x = self.arm[0][1]
                #self.arm[0][0]= MB1 
                self.arm[0][2]= BL_x 
                self.arm[0][3] = RNTI_y
                if CQI_y > 0 : self.arm[0][4]= CQI_y
                else: CQI_y = self.arm[0][4]
                
                self.arm[0][5] = BL_y
                

            
                

            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        return RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y

    


    def send_weight(self, weights, flag):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        
        self.episodeTime += 1
        
        #PUB action
        idx = 0
        str_to_send = ""
        while idx <len(weights):
            str_to_send = str_to_send + str(round(weights[idx],2)) + " "
            idx = idx +1
        
        
        self.index_weight = self.index_weight + 1
        str_to_send = str_to_send + str(self.index_weight) + " "
        str_to_send = str_to_send + str(self.cur_metrics_index) + " "
        str_to_send = str_to_send + str(time.time()) + " "
        

        self.queue_weights.append(str_to_send)
        str_to_send_cur = ""

        if(self.delay_weights >= self.maxdelay_weights ):
            str_to_send_cur = self.queue_weights.pop(0)
            
        else:
            self.delay_weights = self.delay_weights + 1

        
        if(flag == True): print(time.time(), "str_to_send_cur: ", str_to_send_cur, " (rnti1, weight1, rnti2, weight2, WeightIndex, MetricsIndex)")


        self.socket_send_action.send_string(str_to_send_cur)
        # 4. RIC transmits weights to RAN
        
        
    def send_start_RAN(self):
        ''' Send 'start' to RAN to initiate exchanges between RAN and RIC'''
        weights = [70, 0.7, 71, 0.3]
        str_to_send ="start"
        self.socket_send_action.send_string(str_to_send)
                

        print("Sent 'srart' to RAN")

    


    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''
        RNTI1, CQI1, BL1, MB1, RNTI2, CQI2, BL2, MB2 = self.get_state() 
        
        self.arm[0][0] = RNTI1
        self.arm[0][1] = CQI1
        self.arm[0][2] = BL1
        self.arm[0][3] = MB1

        self.arm[0][4] = RNTI2
        self.arm[0][5] = CQI2
        self.arm[0][6] = BL2
        self.arm[0][7] = MB2
        
        
        initialState = np.array(
                [BL1, MB1, CQI1, BL2, MB2, CQI2], dtype=np.double)
                
        
        return initialState

                    
            
            
            
