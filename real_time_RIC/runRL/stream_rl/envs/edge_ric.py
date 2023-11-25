import numpy as np
import pandas as pd
import torch
import gym
from gym.spaces import MultiDiscrete, Box, Discrete
from stream_rl.registry import register_env, create_reward
from ray.rllib.env.env_context import EnvContext
from collections import deque
import random
import zmq
import time

gym.logger.set_level(40)




@register_env("EdgeRIC")
class EdgeRIC(gym.Env):
    """EdgeRIC Env: Simulation of the realtime RIC setup, (2 UEs)"""

    def __init__(self, config: EnvContext):
        self.seed = config["seed"]
        if self.seed != -1:
            random.seed(self.seed)
            np.random.seed(self.seed)
        self.T = config["T"]
        self.t = None
        self.num_UEs = config["num_UEs"]
        self.numArms = config["num_UEs"]
        self.numParams = 3
        self.total_rbgs = config["num_RBGs"]
        self.cqi_map = config["cqi_map"]

        # Delay mechanism
        self.state_delay = config["delay_state"]
        self.action_delay = config["delay_action"]
        self.state_history = deque(
            [np.array([0, 0] * self.num_UEs)] * (self.state_delay + 1),
            maxlen=self.state_delay + 1,
        )
        self.action_history = deque(
            [np.zeros(shape=(self.num_UEs,))] * (self.action_delay + 1),
            maxlen=self.action_delay + 1,
        )

        # Backlog Buffer Elements
        self.max_len_backlog = int(config["base_station"]["max_len"])
        self.backlog_lens = []
        self.backlog_population_params = config["backlog_population"]
        if (
            len(self.backlog_population_params) != self.num_UEs
        ):  # same params to all UEs backlog population
            self.backlog_population_params = [
                self.backlog_population_params
            ] * self.num_UEs

        # CQI Elements
        self.cqis = []
        #self.cqi_traces_df = pd.read_csv(config["cqi_trace"])
        #self.cqi_traces = [
        #    self.cqi_traces_df.iloc[:, ue].tolist() for ue in range(self.num_UEs)
        #]
        #self.cqi_timesteps = [None] * self.num_UEs

        # Action and Observation Space Definitions
        self.action_space = Box(
            low=0.0, high=1.0, shape=(self.num_UEs,), dtype=np.float32
        )
        self.observation_space = Box(
            low=np.array([0, 0, 0] * self.num_UEs),
            high=np.array([self.max_len_backlog, 15, 6000000] * self.num_UEs),
            dtype=np.float32,
        )
        '''
        self.observation_space = Box(
            low=np.array([0, 0] * self.num_UEs),
            high=np.array([self.max_len_backlog, 15] * self.num_UEs),
            dtype=np.float32,
        )
        '''

        self.augment_state_space = config["augment_state_space"]
        if self.augment_state_space:
            self.observation_space = Box(
                low=np.array([0, 0, 0] * self.num_UEs),
                high=np.array(
                    [self.max_len_backlog, 15, 15 * self.max_len_backlog] * self.num_UEs
                ),
                dtype=np.float32,
            )

        self.reward_func = create_reward(config["reward"])
        

        # zmq parameters
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
        


        self.socket_get_mb = self.context.socket(zmq.SUB)
        #self.socket_get_mb.setsockopt(zmq.CONFLATE, 1)
        #self.socket_get_mb.connect("ipc:///tmp/mb_metrics")
        self.socket_get_mb.connect("tcp://172.16.0.2:5558")
        self.socket_get_mb.setsockopt_string(zmq.SUBSCRIBE, "")
        #self.socket_get_mb.setsockopt(zmq.RCVTIMEO, 200)
        self.poller = zmq.Poller()
        self.poller.register(self.socket_get_mb, zmq.POLLIN)


        self.socket_get_mb1 = self.context.socket(zmq.SUB)
        self.socket_get_mb1.setsockopt(zmq.CONFLATE, 1)
        self.socket_get_mb1.connect("ipc:///tmp/mb_metrics1")
        self.socket_get_mb1.setsockopt_string(zmq.SUBSCRIBE, "")
        self.poller1 = zmq.Poller()
        self.poller1.register(self.socket_get_mb1, zmq.POLLIN)

        self.ran_index = 0
        self.curricid = 0
        self.recvdricid = 0
        self.f = 0
        self.f_seq = open("edgeric_seq_2.txt","w")
        self.f_seq_4 = open("edgeric_seq_4.txt","w")

        self.queue_metrics = []
        self.delay_metrics = 0
        self.maxdelay_metrics = 0
        self.queue_weights = []
        self.delay_weights = 0
        self.maxdelay_weights = 0

        self.mbs = []
        self.stall = 0
        self.wts = np.zeros(self.num_UEs*2)

    def reset(self):
        self.t = 0
        self.ran_index = 0
        self.curricid = 0
        self.recvdricid = 0
        self.f = 0
        #RNTIs, CQIs, BLs, tx_bytes = get_metrics_multi(self)
        
        self.backlog_lens = [0] * self.num_UEs
        self.cqis = [1] * self.num_UEs
        '''
        self.cqi_timesteps = [
            random.randint(0, len(self.cqi_traces[ue]) - 1)
            for ue in range(self.num_UEs)
        ]
        self.cqis = [
            self.cqi_traces[ue][self.cqi_timesteps[ue]] for ue in range(self.num_UEs)
        ]
        self.back_pressures = [
            cqi * backlog_len for cqi, backlog_len in zip(self.cqis, self.backlog_lens)
        ]
        '''
        self.mbs = [3000000]*self.num_UEs
        '''
        for ue in range(self.num_UEs):
            self.cqis[ue] = CQIs[ue]
            self.backlog_lens[ue] = BLs[ue]

        '''
        if self.augment_state_space:
            print(self.backlog_lens)
            print(self.cqis)
            print(self.mbs)
            init_state = np.array(
                [
                    param[ue]
                    for ue in range(self.num_UEs)
                    for param in (self.backlog_lens, self.cqis, self.back_pressures)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BP1, BL2, CQI2, BP2.....]
        else:
            init_state = np.array(
                [
                    param[ue]
                    for ue in range(self.num_UEs)
                    for param in (self.backlog_lens, self.cqis, self.mbs)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BL2, CQI2,.....]

        self.state_history.append(init_state)
        return self.state_history[0]

    def step(self, action, RNTIs, CQIs, BLs, tx_bytes, MBs):
        """Order of operations within a step - transfers from :
        1.) Cloud to backlog buffer
        2.) Backlog buffer to playback buffer
        """


        action = np.clip(
            action, a_min=0.00000001, a_max=1.0
        )  # Project action back to action space + add epsilon to prevent divide by zero error

        # Add delay to action
        self.action_history.append(action)
        action = self.action_history[0]

        # Update time
        self.t += 1
        #RNTIs, CQIs, BLs, tx_bytes = self.get_metrics_multi(self)
        weight = np.zeros(self.num_UEs*2)
        # Update CQI for all UEs according to trace
        total_bytes_transferred = 0
        for ue in range(self.num_UEs):

            
            self.mbs[ue] = MBs[ue]
            #self.cqi_timesteps[ue] += 1
            #self.cqi_timesteps[ue] %= len(self.cqi_traces[ue])
            #self.cqis[ue] = self.cqi_traces[ue][self.cqi_timesteps[ue]]
            self.cqis[ue] = CQIs[ue]
            
            # Update BLs
            inter_arrival_time, chunk_size = self.backlog_population_params[ue]
            self.backlog_lens[ue] = BLs[ue]


            '''
            if self.t % inter_arrival_time == 0:
                self.backlog_lens[ue] += chunk_size
                self.backlog_lens[ue] = min(self.backlog_lens[ue], self.max_len_backlog)
            '''

            # Compute RBGs allocated for this UE
            percentage_RBG = action[ue] / sum(action)
            print(action[ue])
            weight[ue*2+1] = percentage_RBG
            weight[ue*2] = RNTIs[ue]

            #percentage_RBG = action[ue]
            #allocated_RBG = int(percentage_RBG * self.total_rbgs)

            # Transfer data from BL to UE
            '''
            mean, std = self.cqi_map[self.cqis[ue]]
            bytes_transferred = (
                allocated_RBG
                * np.random.normal(mean, std)
                # * np.random.binomial(1, 0.9)  # BLER 10%
                * 1000
            ) // 8
            bytes_transferred = min(bytes_transferred, self.backlog_lens[ue])
            total_bytes_transferred += bytes_transferred
            self.backlog_lens[ue] -= bytes_transferred
            '''

        #reward = self.reward_func(total_bytes_transferred, self.backlog_lens)
        reward = self.reward_func(tx_bytes, self.backlog_lens, self.stall)
        #reward = tx_bytes
        print(reward)
        self.stall = 0
        if self.augment_state_space:
            self.back_pressures = [
                cqi * backlog_len
                for cqi, backlog_len in zip(self.cqis, self.backlog_lens)
            ]
            next_state = np.array(
                [
                    param[ue]
                    for ue in range(self.num_UEs)
                    for param in (self.backlog_lens, self.cqis, self.back_pressures)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BP1, BL2, CQI2, BP2,.....]
        else:
            next_state = np.array(
                [
                    param[ue]
                    for ue in range(self.num_UEs)
                    for param in (self.backlog_lens, self.cqis, self.mbs)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BL2, CQI2,.....]

        done = self.t == self.T
        info = {}
        flag = True
        self.wts = weight
        self.send_weight(weight, flag)
        self.state_history.append(next_state)  # Add delay to state observation
        return self.state_history[0], reward, done, info



    def get_metrics_multi(self):
        #ZMQ sub
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
            #self.recvdricid = int(messagedata[numParams*self.numArms])
            #self.recvdricid = int(messagedata[numParams*self.numArms + self.numArms*2])
            self.recvdricid = int(messagedata[numParams*self.numArms + self.numArms*2])

            print(f'received RIC ID:', self.recvdricid, self.curricid)

            
            while(self.curricid-self.recvdricid>1 and self.f==1):
            #    string_temp = self.socket_get_state.recv()
                string = self.socket_get_state.recv()
                messagedata= string.split()
                self.recvdricid = int(messagedata[numParams*self.numArms + self.numArms*2])
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

            messagedata= string.split() 
            #if(len(messagedata)):

            #print("string", string, len(messagedata))
            
            #print(messagedata[0], messagedata[1], messagedata[2])
            RNTIs = np.zeros(self.numArms)
            CQIs = np.zeros(self.numArms)
            BLs = np.zeros(self.numArms)
            txb = 0
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


                msg_data_str = str(messagedata[numParams*self.numArms+ self.numArms*2 +2])
                #print(msg_data_str)
                _frst = msg_data_str.find("'") + 1
                _last = msg_data_str.find("\\")
                msg_data_int = int(msg_data_str[_frst:_last])

                self.ran_index = msg_data_int
                #print("RAN index is" + str(self.ran_index))
                txb = float(messagedata[(self.numArms*self.numParams) + (self.numArms *2) +1])

                #self.ran_index = (messagedata[numParams*self.numArms])

                for i in range(self.numArms):
                    RNTIs[i] = int(messagedata[i*numParams+0])
                    CQIs[i] = int(messagedata[i*numParams+1])
                    BLs[i] = int(messagedata[i*numParams+2]) 
                    string_mb = " "
                    if RNTIs[i] == 00:
                        events = self.poller.poll(0.1) # 0.2 ms timeout in milliseconds
                        if events:
                            string_mb = self.socket_get_mb.recv()
                        '''    
                        try:
                            string_mb = self.socket_get_mb.recv()
                        except zmq.error.Again:
                            print("No message received in the last 0.1ms." + "\n")
                        '''
                        print(str(string_mb))
                        print(len(string_mb))
                        if len(string_mb) < 4:
                            print("empty")
                            MBs[i] = self.mbs[i]
                            print(MBs[i])
                            self.stall = self.stall+0
                        else:
                            string_mb = string_mb.decode()
                            print(string_mb)
                            string_mb = string_mb.split() 
                            print(string_mb)
                            MBs[i] = int(string_mb[0])
                            self.stall = self.stall+int(string_mb[1])
                            
                    elif RNTIs[i] == 91:
                        events = self.poller1.poll(0.1) # 0.2 ms timeout in milliseconds
                        if events:
                            string_mb = self.socket_get_mb1.recv()
                        '''    
                        try:
                            string_mb = self.socket_get_mb.recv()
                        except zmq.error.Again:
                            print("No message received in the last 0.1ms." + "\n")
                        '''
                        print(str(string_mb))
                        print(len(string_mb))
                        if len(string_mb) < 4:
                            print("empty")
                            MBs[i] = self.mbs[i]
                            print(MBs[i])
                            self.stall = self.stall+0
                        else:
                            string_mb = string_mb.decode()
                            print(string_mb)
                            string_mb = string_mb.split() 
                            print(string_mb)
                            MBs[i] = int(string_mb[0])
                            self.stall = self.stall+int(string_mb[1])
                    
                    else:
                        print(str(RNTIs[i]) + " " + "it is nothing" + "\n")
                        MBs[i] = 3000000
                        #self.stall = self.stall + 0
                        #print(self.wts)
                        if RNTIs[i] in self.wts:
                            #index = self.wts.index(RNTIs[i])
                            index = np.where(self.wts == RNTIs[i])[0][0]
                            wght = self.wts[index + 1]
                            if wght>0.01:
                                self.stall = self.stall + 2
                        else:
                            self.stall = self.stall+0
                        
                      


                    
                        

                   
                         
                    
                '''   
                for i in range(self.numArms):
                    self.arm[0][i*numParams+0] = RNTIs[i]            
                    if CQIs[i] > 0 : self.arm[0][i*numParams+1] = CQIs[i]
                    else:  CQIs[i] = self.arm[0][i*numParams+1]
                    self.arm[0][i*numParams+2] = BLs[i]
                '''
                #print(self.arm[0][1],self.arm[0][3]) 
                
            
            #print(RNTIs)
            #print(CQIs)
            #print(BLs)
            #print(txb)    

            
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()
                print("blimey")


        
        return RNTIs, CQIs, BLs, txb, MBs

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
            self.socket_send_action.send_string(str_to_send_cur)
            #self.delay_weights = 0
        else:
            self.delay_weights = self.delay_weights + 1
        
        
        seq_4 = str(time.time()) + ",\t" + str_to_send_cur  
        seq_4 = seq_4.replace("b'", "")
        seq_4 = seq_4.replace(" ", ",\t")
        seq_4 = seq_4.replace("\\x00'","")

        self.f_seq_4.write(seq_4)

        

        if(flag == True): print("str_to_send_cur: ", str_to_send_cur)


        # 4. RIC sends to RAN: weight + tti index for which weight is being sent 
        #self.socket_send_action.send_string(str_to_send_cur)
    


    
