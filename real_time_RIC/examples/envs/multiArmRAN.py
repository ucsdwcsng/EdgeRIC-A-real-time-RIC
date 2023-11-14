'''
Environment to calculate the Whittle index values as a deep reinforcement 
learning environment modelled after the OpenAi Gym API.
Same mini-batch episodes have the same trajectory values for comparing their returns.
This is the down-link environment.
'''
#export PYTHONPATH=$PYTHONPATH:/home/wcsng-24/.local/lib/python3.8/site-packages

from collections import defaultdict
from email.policy import default
from typing import DefaultDict
import sys
#sys.path.append('/home/wcsng-24/.local/lib/python3.8/site-packages/gym')


import gym
import math
import sys

import zmq

import time
import random
#import datetime
import numpy as np
import pandas as pd
from gym import spaces
# from numpy.random import RandomState
# from torch import arange
#from stable_baselines.common.env_checker import check_env #this test throws errors and needs tensorflow 1.x with python 3.6. it's normal
import zmq
import time
import datetime
from datetime import datetime
#df=open('text file','w')
#ptime = datetime.now()

class multiArmRAN(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize, episodeLimit, fixedSizeMDP, noiseVar, cost=0, zmq_params=None, numArms= 2):

        super(multiArmRAN, self).__init__()
        # self.seed = seed
        self.cost = cost
        # self.myRandomPRNG = random.Random(self.seed)
        # self.G = np.random.RandomState(self.seed) # create a special PRNG for a class instantiation
        # self.classVal = -1
        self.numArms =numArms
        self.numParams = 3   # RNTI, CQI, Backlog
        self.scheduleArms =1
        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0
        self.currentEpisode = 0
        self.noiseVar = noiseVar
        #self.ptime = ptime

        self.rate = r1
        self.maxBufferSize = maxBufferSize  # 500
        self.high_RB = high_RB  # Dummy
        self.low_RB = low_RB  # Dummy
        #self.arm = {0: [1, 1, 1, 1]}  # [Media buffer 1, CQI 1, MB2, CQI 2]
        
        #self.arm = {0: [0, 0, 0, 0, 0, 0]}  # [RNTI 1, CQI 1, Backlog 1, RNTI 2, CQI 2, Backlog 2]
        self.arm = {0:  np.zeros(self.numArms*3, dtype=np.double)}  # [RNTI 1, CQI 1, Backlog 1, RNTI 2, CQI 2, Backlog 2, ...]

        self.train = Training
        self.batchSize = batchSize
        self.miniBatchCounter = 0
        self.episodeLimit = episodeLimit
        self.fixedSizeMDP = fixedSizeMDP
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - All zmq socket inits are here
        #zmq inits
        # zmq_params = zmq_params # <<<<<<<<<< Raini Extract any info needed for socket inits here (info that's passed from multiArmWrapper.py)
        # for pubbing action
        self.context = zmq.Context()
        print("zmq context created")

        self.socket_send_action = self.context.socket(zmq.PUB)
        self.socket_send_action.bind("ipc:///tmp/socket_weights")

        # for subbing state
        #int conflate = 1
        self.socket_get_state = self.context.socket(zmq.SUB)
        self.socket_get_state.setsockopt(zmq.CONFLATE, 1)
        self.socket_get_state.connect("ipc:///tmp/socket_metrics")
        
        self.socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")
        

        ##self.socket_mbuff = self.context.socket(zmq.SUB)
        ##self.socket_mbuff.bind("tcp://172.16.0.1:5556")
        ##self.socket_mbuff.setsockopt_string(zmq.SUBSCRIBE, "")

        ##self.socket_mbuff_1 = self.context.socket(zmq.SUB)
        ##self.socket_mbuff_1.bind("tcp://172.16.0.1:5566")
        ##self.socket_mbuff_1.setsockopt_string(zmq.SUBSCRIBE, "")

        
        ##self.socket_reset = self.context.socket(zmq.PUB)
        ##self.socket_reset.bind("tcp://172.16.0.1:5557")
        ##self.zmq_params = zmq_params
        self.queue_metrics = []
        self.delay_metrics = 0
        self.maxdelay_metrics = 0
        self.queue_weights = []
        self.delay_weights = 0
        self.maxdelay_weights = 0
        self.high_weight = 0.9
        self.low_weight = 0.1


        self.ran_index = 0

        #self.f_seq = open("edgeric_seq_2.txt","w")
        #self.f_seq_4 = open("edgeric_seq_4.txt","w")
        self.ran_index = 0
        self.curricid = 0
        self.recvdricid = 0
        self.f = 0



        

        
        

        ## get some rnti

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Raini - End of zmq inits >>>>>>>>>>>>>>>>>>

        #self.observationSize = 4
        self.observationSize = self.numArms*2
        
        lowState = np.zeros(self.observationSize, dtype=np.double)
        #highState = np.full(self.observationSize, [
        #                    self.maxBufferSize, 15, self.maxBufferSize, 15], dtype=np.double)
        
        #highState = np.full(self.observationSize, [
        #                    self.maxBufferSize, 15, self.maxBufferSize, 15], dtype=np.double)
        highState = lowState
        for i in range(self.numArms): 
            highState[i] = self.maxBufferSize
            highState[i*2+1] = 15

        #self.action_space = spaces.Discrete(2)
        self.action_space = spaces.Discrete(9)
        #self.action_space = spaces.Box(np.array([0,0]), np.array([1,1]), dtype=np.double)
        self.observation_space = spaces.Box(
            lowState, highState, dtype=np.double)


    # def _createActionTable(self):
    #     '''function that creates a mapping of actions to take. Will be mapped with the action taken from the agent.'''
        
    #     self.actionTable  = list(itertools.product([0, 1], repeat=self.numArms))
    #     self.actionTable = [x for x in self.actionTable if  sum(x) == self.scheduleArms]
    #     self.action_space = spaces.Discrete(len(self.actionTable))


    # def negotiate_rnti(self):

    #     print("receiving from mbuff...")
    #     mbuff_message = self.socket_mbuff.recv()
    #     self.rnti = int((mbuff_message.split())[0])
    #     print("...done, got " + str(self.rnti))
    #     if self.zmq_params == 1:
        
    #         self.socket_inproc = self.context.socket(zmq.REP)
        
    #         self.socket_inproc.bind("tcp://*:5559")
    #         their_rnti = int(self.socket_inproc.recv())
    #         self.socket_inproc.send_string("")
    #         while True:
    #             if their_rnti != self.rnti:
    #                 print("negotiated " + str(their_rnti) + " for UE1")
    #                 print("negotiated " + str(self.rnti) + " for UE2")
    #                 break
    #             mbuff_message = self.socket_mbuff.recv()
    #             self.rnti = int((mbuff_message.split())[0])
    #     else:
    #         self.socket_inproc = self.context.socket(zmq.REQ)
    #         self.socket_inproc.connect("tcp://localhost:5559")
    #         self.socket_inproc.send_string(str(self.rnti))
    #         self.socket_inproc.recv()

    # def _findStateIndex(self, state):

    #     stateLocation = np.where((self.stateArray == state).all(axis=1))[0][0]
    #     return stateLocation
    
    
    
    def _calReward(self, action, curState, nextState):
        ''' function to calculate next state, and reward given the action'''
        # state = [ BL1, CQI1, BL2, CQI2]
        total_reward = 0
        
        total_reward = -(nextState[0] + nextState[2])/self.maxBufferSize; 
        
        '''
        diffState = nextState - curState

        threshold = 400000 ; 
        ratio = 0.01; 
        reward = 0
        
        
        if(diffState[0] +diffState[2] < 0):
            reward = -(diffState[0] +diffState[2])
        reward += (threshold - (curState[0] + curState[2]))*ratio

        cost = 0
        step_cost= 1
        if curState[1] < curState[3] and action == 0: cost += step_cost
        if curState[1] > curState[3] and action == 1: cost += step_cost

        total_reward = reward - cost
        '''

        return total_reward

    # def _normalizeState(self, state):
    #     ''' Function for normalizing the remaining load against the max load value'''
    #     state[0] = state[0] / self.maxBufferSize
    #     state[1] = state[1] / 15.0
    #     return state

    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)
        ##assert action in [0, 1]
        # self.time += 1
        self.episodeTime += 1
        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        # nextState, reward = self._calReward(action)

        #PUB action
        # action = 1
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - sending action to ran. action=1 corresponds to requesting high_rb for this UE (and 0 low_RB)
        

        #str_to_send = str(action) # to check the string 
        #str_to_send = str(action) # to check the string 
        #self.socket_send_action.send_string(str_to_send)
        #print("step", action)
        self.send_action(action)

        done = self.episodeTime == self.episodeLimit

        # get next state
        #MB1,CQI1,MB2,CQI2, = self.get_state() 
        RNTI1, CQI1, BL1, RNTI2, CQI2, BL2 = self.get_state() # to make 


        # while MB == -1:
        #     CQI,MB = self.get_state()
        curState = np.array([self.arm[0][2], self.arm[0][1], self.arm[0][5], self.arm[0][4]], dtype=np.double)
        
        self.arm[0][0] = RNTI1
        self.arm[0][1] = CQI1
        self.arm[0][2] = BL1
        self.arm[0][3] = RNTI2
        self.arm[0][4] = CQI2
        self.arm[0][5] = BL2
        
        #nextState = np.array([CQI1, BL1, CQI2, BL2], dtype=np.double)
        nextState = np.array([BL1, CQI1, BL2, CQI2], dtype=np.double)
        # nextState = self._normalizeState(nextState)

        # if done:
        #reward = self._calReward(MB1,MB2 )
        #reward = self._calReward(BL1,BL2 )
        reward = self._calReward(action, curState, nextState )

        #print("in step action: ", action, " reward: ", reward, " curState: ", curState, " nextState: ", nextState)
        ##print()

        info = {}
        done = False
        return nextState, reward, done, info

    def get_state(self):
        #ZMQ sub
        string = ""
        # print("mark1")
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            string_temp = self.socket_get_state.recv()
            #print("temp: ", string_temp)

            self.queue_metrics.append(string_temp)
            
            if(self.delay_metrics >= self.maxdelay_metrics ):
                string = self.queue_metrics.pop(0)
                #self.delay_metrics = 0
            else:
                self.delay_metrics = self.delay_metrics + 1

            



            messagedata= string.split() 
            #if(len(messagedata)print(string)
            #print("string", string, len(messagedata))
            
            #print(messagedata[0], messagedata[1], messagedata[2])
            
            
            RNTI_x = self.arm[0][0]            
            CQI_x = self.arm[0][1]
            #MB1 = self.arm[0][0]
            BL_x = self.arm[0][2]            
            RNTI_y = self.arm[0][3]
            CQI_y = self.arm[0][4]
            #MB2 = self.arm[0][2]
            BL_y = self.arm[0][5]
            
            # self.episodeTime = 0
            
            if len(messagedata) >= 6:
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract CQI
                RNTI_x = int(messagedata[0])
                if int(messagedata[1]) > 0 : CQI_x =  int(messagedata[1]) 
                BL_x = int(messagedata[2])
                RNTI_y = int(messagedata[3])
                if int(messagedata[4]) > 0 : CQI_y =  int(messagedata[4]) 
                BL_y = int(messagedata[5])
                
            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        ###print("in get_state state: ",RNTI_x,CQI_x, BL_x, RNTI_y, CQI_y, BL_y )

        return RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y
    
    def send_action(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        # self.time += 1
        self.episodeTime += 1
        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        # nextState, reward = self._calReward(action)

        #PUB action
        # action = 1
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - sending action to ran. action=1 corresponds to requesting high_rb for this UE (and 0 low_RB)
        '''
        if (action = 0 and action < 5):
            weight1 = self.high_weight
            weight2 = self.low_weight
        else:
            weight1 = self.low_weight
            weight2 = self.high_weight
        '''
        #print("send_action", action)
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
        RNTI2 =self.arm[0][3] 

        weights = [int(RNTI1), weight1, int(RNTI2), weight2]
        #print("send_action", weights)

        idx = 0
        str_to_send = ""
        while idx <len(weights):
            str_to_send = str_to_send + str(round(weights[idx],2)) + " "
            idx = idx +1
        #str_to_send = str_to_send+ "\n"
        
        #print("str_to_send: ", str_to_send)

        self.queue_weights.append(str_to_send)
        str_to_send_cur = ""

        if(self.delay_weights >= self.maxdelay_weights ):
            str_to_send_cur = self.queue_weights.pop(0)
            #self.delay_weights = 0
        else:
            self.delay_weights = self.delay_weights + 1
        
        #print("in send_action str_to_send_cur: ", str_to_send_cur)

        self.socket_send_action.send_string(str_to_send_cur)


        
    ###### Added for weight-based scheduling by whko  ####
    def dummy(self):
        ''' Standard Gym function for supplying initial episode state.'''
        print("testing")
        
    
    '''
    def get_metrics_multi(self):
        #ZMQ sub
        string = ""
        # print("mark1")
        #f = 0
        if(self.recvdricid>1):
            self.f=1

        self.curricid+=1
        numParams = self.numParams
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            string_recv = self.socket_get_state.recv()
            print(string_recv)
            messagedata= string_recv.split()
            self.recvdricid = int(messagedata[numParams*self.numArms])

            #self.curricid+=1
            #recvdricid = self.curricid-2;
            #recvdricid = 0;
            
            while(self.curricid-self.recvdricid>1 and self.f==1):
            #    string_temp = self.socket_get_state.recv()
                string = self.socket_get_state.recv()
                messagedata= string.split()
                self.recvdricid = int(messagedata[numParams*self.numArms])
                string_recv = string
            #    print(self.curricid, recvdricid)
            #    string_recv = string

            
            

            #print("temp: ", string_temp)
            # 2. RIC received state information from RAN: UE metrics + tti index


            
            string_temp = string_recv
            string_temp = str(string_temp).replace(" ", ",\t")
            string_temp = str(string_temp).replace("b'", "")
            string_temp = str(string_temp).replace("\\x00'","")
            seq_2 = str(time.time()) + ",\t" + str(string_temp) + ",\t" + str(self.curricid) + ",\t" + str(self.recvdricid) + "\n"
            self.f_seq.write(seq_2)

            #seq_2 = str(time.time()) + ",\t" + str(string_temp) + "2 \n"
            #self.f_seq.write(seq_2)


            



            self.queue_metrics.append(string_recv)
            
            if(self.delay_metrics >= self.maxdelay_metrics ):
                string = self.queue_metrics.pop(0)
                #self.delay_metrics = 0
            else:
                self.delay_metrics = self.delay_metrics + 1

            print("recved string: ", string)

            
            #timestamp = datetime.now()
            #nowhour = timestamp.hour
            #nowmin = timestamp.minute + nowhour*60
            #nowsec = (timestamp.second + nowmin*60)
            #nowmicrosec = timestamp.microsecond 
            #nowtime = nowsec*1000000+nowmicrosec
            #self.ptime = timestamp
            #print(nowtime)

            #df.write(str(nowtime))
            #df.write(' ')
            #df.write(str(string))
            #df.write(' ')

            

            messagedata= string.split() 
            #if(len(messagedata)):

            #print("string", string, len(messagedata))
            
            #print(messagedata[0], messagedata[1], messagedata[2])
            RNTIs = np.zeros(self.numArms)
            CQIs = np.zeros(self.numArms)
            BLs = np.zeros(self.numArms)
             
            for i in range(self.numArms):
                RNTIs[i] = self.arm[0][i*numParams+0]            
                CQIs[i] = self.arm[0][i*numParams+1]
                BLs[i] = self.arm[0][i*numParams+2]            
            
            
            # self.episodeTime = 0
            
            if len(messagedata) >= self.numArms*self.numParams:
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract CQI


                msg_data_str = str(messagedata[numParams*self.numArms+2])
                _frst = msg_data_str.find("'") + 1
                _last = msg_data_str.find("\\")
                msg_data_int = int(msg_data_str[_frst:_last])




                self.ran_index = msg_data_int

                #self.ran_index = (messagedata[numParams*self.numArms])

                for i in range(self.numArms):
                    RNTIs[i] = int(messagedata[i*numParams+0])
                    CQIs[i] = int(messagedata[i*numParams+1])
                    BLs[i] = int(messagedata[i*numParams+2])        
            
                    
                for i in range(self.numArms):
                    self.arm[0][i*numParams+0] = RNTIs[i]            
                    if CQIs[i] > 0 : self.arm[0][i*numParams+1] = CQIs[i]
                    else:  CQIs[i] = self.arm[0][i*numParams+1]
                    self.arm[0][i*numParams+2] = BLs[i]
                
                #print(self.arm[0][1],self.arm[0][3]) 
                

            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        return RNTIs, CQIs, BLs
    '''

    def get_metrics_multi(self):
        #ZMQ sub
        RNTIs = []
        CQIs = []
        BLs = []
        tx = 0

        string = " "
        # print("mark1")
        #f = 0
        if(self.recvdricid>1):
            self.f=1

        self.curricid+=1
        numParams = self.numParams
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            string_recv = self.socket_get_state.recv()
            print(string_recv)
            messagedata= string_recv.split()
            self.recvdricid = int(messagedata[numParams*self.numArms + self.numArms*2])

            print(f'received RIC ID:', self.recvdricid, self.curricid)

            
            while(self.curricid-self.recvdricid>1 and self.f==1):
                #sys.exit()
            #    string_temp = self.socket_get_state.recv()
                string = self.socket_get_state.recv()
                messagedata= string.split()
                self.recvdricid = int(messagedata[numParams*self.numArms + self.numArms*2])
                string_recv = string
            #    print(self.curricid, recvdricid)
            #    string_recv = string

            #print("temp: ", string_temp)
            # 2. RIC received state information from RAN: UE metrics + tti index

            #print("out of while")
            string_temp = string_recv
            string_temp = str(string_temp).replace(" ", ",\t")
            string_temp = str(string_temp).replace("b'", "")
            string_temp = str(string_temp).replace("\\x00'","")
            seq_2 = str(time.time()) + ",\t" + str(string_temp) + ",\t" + str(self.curricid) + ",\t" + str(self.recvdricid) + "\n"
            #self.f_seq.write(seq_2)

            #seq_2 = str(time.time()) + ",\t" + str(string_temp) + "2 \n"
            #self.f_seq.write(seq_2)

            self.queue_metrics.append(string_recv)
            
            if(self.delay_metrics >= self.maxdelay_metrics ):
                string = self.queue_metrics.pop(0)
                #self.delay_metrics = 0
            else:
                self.delay_metrics = self.delay_metrics + 1

            #print("recved string: ", string)
            #print("messagesata: ", messagedata)

            messagedata= string.split() 
            #if(len(messagedata)):
            #print(messagedata)

            #print("string", string, len(messagedata))
            
            #print(messagedata[0], messagedata[1], messagedata[2])
            RNTIs = np.zeros(self.numArms)
            CQIs = np.zeros(self.numArms)
            BLs = np.zeros(self.numArms)
            txs = np.zeros(self.numArms)
            MBs = np.zeros(self.numArms)
            
            '''
            for i in range(self.numArms):
                RNTIs[i] = self.arm[0][i*numParams+0]            
                CQIs[i] = self.arm[0][i*numParams+1]
                BLs[i] = self.arm[0][i*numParams+2]            
            
            '''
            # self.episodeTime = 0
            
            if len(messagedata) >= self.numArms*self.numParams:
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract CQI

                #print("entered if statement")
                msg_data_str = str(messagedata[numParams*self.numArms+ self.numArms*2 +2])
                _frst = msg_data_str.find("'") + 1
                _last = msg_data_str.find("\\")
                msg_data_int = int(msg_data_str[_frst:_last])

                self.ran_index = msg_data_int
                #txb = float(messagedata[self.numArms*self.numParams+1])

                #self.ran_index = (messagedata[numParams*self.numArms])

                for i in range(self.numArms):
                    RNTIs[i] = int(messagedata[i*numParams+0])
                    CQIs[i] = int(messagedata[i*numParams+1])
                    BLs[i] = int(messagedata[i*numParams+2]) 
                    for j in range(self.numArms):
                        if int(messagedata[self.numArms*numParams+j*2]) == RNTIs[i]:
                            txs[i] = float(messagedata[self.numArms*numParams+j*2+1])
                            break 

                    #txs[i] = int(messagedata[i*numParams+3]) 
                    '''
                    if self.RNTIs[i] == self.r:
                        RNTI = self.RNTIs[i]
                        CQI = CQIs[i]
                        BL = BLs[i]
                        tx = txs[i] '''
            
            #print(RNTI)
            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        #print("RNTI, CQI, BL (get metrics func): " + str(RNTI) + str(CQI) + str(BL))
        #print(RNTIs)
        return RNTIs, CQIs, BLs




    def get_metrics(self):
        #ZMQ sub
        string = ""
        # print("mark1")
        try:

            # Every 1ms  - recieve info from RAN (blocking)
            string_temp = self.socket_get_state.recv()
            #print("temp: ", string_temp)

            self.queue_metrics.append(string_temp)
            
            if(self.delay_metrics >= self.maxdelay_metrics ):
                string = self.queue_metrics.pop(0)
                #self.delay_metrics = 0
            else:
                self.delay_metrics = self.delay_metrics + 1

            #print("string: ", string)



            messagedata= string.split() 
            #if(len(messagedata)print(string)
            #print("string", string, len(messagedata))
            
            #print(messagedata[0], messagedata[1], messagedata[2])
            
            
            RNTI_x = self.arm[0][0]            
            CQI_x = self.arm[0][1]
            #MB1 = self.arm[0][0]
            BL_x = self.arm[0][2]            
            RNTI_y = self.arm[0][3]
            CQI_y = self.arm[0][4]
            #MB2 = self.arm[0][2]
            BL_y = self.arm[0][5]
            
            # self.episodeTime = 0
            
            if len(messagedata) >= 6:
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract CQI
                RNTI_x = int(messagedata[0])
                CQI_x = int(messagedata[1])
                BL_x = int(messagedata[2])
                RNTI_y = int(messagedata[3])
                CQI_y = int(messagedata[4])
                BL_y = int(messagedata[5])
                
                
                ##if RNTI_x < RNTI_y:
                ##    CQI1 = CQI_x
                ##    CQI2 = CQI_y
                ##else:
                ##    CQI1= CQI_y
                ##    CQI2= CQI_x
                    
                self.arm[0][0] = RNTI_x
                if CQI_x > 0 : self.arm[0][1]= CQI_x
                else:  CQI_x = self.arm[0][1]
                #self.arm[0][0]= MB1 
                self.arm[0][2]= BL_x 
                self.arm[0][3] = RNTI_y
                if CQI_y > 0 : self.arm[0][4]= CQI_y
                else: CQI_y = self.arm[0][4]
                #self.arm[0][2] = MB2
                self.arm[0][5] = BL_y
                #print(self.arm[0][1],self.arm[0][3]) 
                

            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        return RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y

    

    '''
    def send_weight(self, weights, flag):
        #Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.
        # self.time += 1
        self.episodeTime += 1
        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        # nextState, reward = self._calReward(action)

        #PUB action
        # action = 1
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - sending action to ran. action=1 corresponds to requesting high_rb for this UE (and 0 low_RB)
        #print(weights)
        idx = 0
        str_to_send = ""
        while idx <len(weights):
            str_to_send = str_to_send + str(round(weights[idx],4)) + " "
            idx = idx +1
        #str_to_send = str_to_send+ "\n"

        str_to_send = str_to_send + str(self.curricid) + " " + str(self.ran_index) + " " + "\n"

        #str_to_send = str_to_send + str(self.ran_index) + "\n"


        
        print("str_to_send: ", str_to_send)
        #myfile.write('%s\n", str_to_send)

        #seq_4 = str(time.time()) + ",\t" + str_to_send + "\n"
        #self.f_seq_4.write(seq_4)


        self.queue_weights.append(str_to_send)
        str_to_send_cur = ""

        if(self.delay_weights >= self.maxdelay_weights ):
            str_to_send_cur = self.queue_weights.pop(0)
            #self.delay_weights = 0
        else:
            self.delay_weights = self.delay_weights + 1
        
        
        seq_4 = str(time.time()) + ",\t" + str_to_send_cur  
        seq_4 = seq_4.replace("b'", "")
        seq_4 = seq_4.replace(" ", ",\t")
        seq_4 = seq_4.replace("\\x00'","")

        self.f_seq_4.write(seq_4)

        

        if(flag == True): print("str_to_send_cur: ", str_to_send_cur)

        
        #timestamp = datetime.now()
        #nowhour = timestamp.hour
        #nowmin = timestamp.minute + nowhour*60
        #nowsec = (timestamp.second + nowmin*60)
        #nowmicrosec = timestamp.microsecond 
        #nowtime = nowsec*1000000+nowmicrosec
        #self.ptime = timestamp
        #print(nowtime)

        #df.write(str(nowtime))
        #df.write(' ')
        #df.write(str_to_send_cur)
        #df.write('\n')
        

        # 4. RIC sends to RAN: weight + tti index for which weight is being sent 
        self.socket_send_action.send_string(str_to_send_cur)

    '''


    def send_weight(self, weights, flag):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        # self.time += 1
        #self.episodeTime += 1
        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        # nextState, reward = self._calReward(action)

        #PUB action
        # action = 1
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - sending action to ran. action=1 corresponds to requesting high_rb for this UE (and 0 low_RB)
        #print(weights)
        flag = True
        #print("hey there")
        #print(flag)
        #print(weights)
        idx = 0
        str_to_send = ""
        while idx <len(weights):
            str_to_send = str_to_send + str(round(weights[idx],4)) + " "
            idx = idx +1
        #str_to_send = str_to_send+ "\n"

        str_to_send = str_to_send + str(self.curricid) + " " + str(self.ran_index) + " " + "\n"

        #str_to_send = str_to_send + str(self.ran_index) + "\n"


        
        #print("str_to_send: ", str_to_send)
        #myfile.write('%s\n", str_to_send)

        #seq_4 = str(time.time()) + ",\t" + str_to_send + "\n"
        #self.f_seq_4.write(seq_4)

        try:
            self.queue_weights.append(str_to_send)
            str_to_send_cur = ""

            if(self.delay_weights >= self.maxdelay_weights ):
                str_to_send_cur = self.queue_weights.pop(0)
                #if(flag == True): print("str_to_send_cur: ", str_to_send_cur)
                self.socket_send_action.send_string(str_to_send_cur)
                
                #self.delay_weights = 0
            else:
                self.delay_weights = self.delay_weights + 1
         
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")
        
        seq_4 = str(time.time()) + ",\t" + str_to_send_cur  
        seq_4 = seq_4.replace("b'", "")
        seq_4 = seq_4.replace(" ", ",\t")
        seq_4 = seq_4.replace("\\x00'","")

        #self.f_seq_4.write(seq_4)

        

        if(flag == True): print("str_to_send_cur: ", str_to_send_cur)
        #self.socket_send_action.send_string(str_to_send_cur)
        #self.socket_send_action2.send_string(str_to_send_cur)

    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''
        #print("reset reached????")
        # self.start = None
        RNTI1, CQI1, BL1, RNTI2, CQI2, BL2 = self.get_state() # to make 
        # print("crossed")
        # while MB == -1:
        #     CQI,MB = self.get_state()
        self.arm[0][0] = RNTI1
        self.arm[0][1] = CQI1
        self.arm[0][2] = BL1
        self.arm[0][3] = RNTI2
        self.arm[0][4] = CQI2
        self.arm[0][5] = BL2
        # if self.miniBatchCounter % self.batchSize == 0:

        #     self.miniBatchCounter = 0

        initialState = np.array(
                [self.arm[0][2], self.arm[0][1], self.arm[0][5],self.arm[0][4]], dtype=np.double)
                
        # initialState = self._normalizeState(initialState)

        # self.miniBatchCounter += 1

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - send reset signal so that udp_client can reset its MB length (to ideally a random value between 10% and 20% max MB capacity)
        #####self.socket_reset.send_string(str("All reset"))

        return initialState

                    
            
            
            
