'''
Environment to calculate the Whittle index values as a deep reinforcement 
learning environment modelled after the OpenAi Gym API.
Same mini-batch episodes have the same trajectory values for comparing their returns.
This is the down-link environment.
'''

from collections import defaultdict
from email.policy import default
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
# from numpy.random import RandomState
# from torch import arange
#from stable_baselines.common.env_checker import check_env #this test throws errors and needs tensorflow 1.x with python 3.6. it's normal
import zmq
import time


class downLinkEnvProtoRAN(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize, episodeLimit, fixedSizeMDP, noiseVar, cost, zmq_params=None):

        super(downLinkEnvProtoRAN, self).__init__()
        # self.seed = seed
        self.cost = cost
        # self.myRandomPRNG = random.Random(self.seed)
        # self.G = np.random.RandomState(self.seed) # create a special PRNG for a class instantiation
        # self.classVal = -1

        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0
        self.currentEpisode = 0
        self.noiseVar = noiseVar

        self.rate = r1
        self.maxBufferSize = maxBufferSize  # 500
        self.high_RB = high_RB  # Dummy
        self.low_RB = low_RB  # Dummy
        self.arm = {0: [1, 1]}  # [Media buffer, CQI]

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
        self.socket_get_state = self.context.socket(zmq.SUB)
        self.socket_get_state.connect("ipc:///tmp/socket_metrics")

        self.socket_get_state.setsockopt_string(zmq.SUBSCRIBE, "")

        self.socket_mbuff = self.context.socket(zmq.SUB)
        self.socket_mbuff.bind("tcp://172.16.0.1:5556")
        self.socket_mbuff.setsockopt_string(zmq.SUBSCRIBE, "")

        self.socket_reset = self.context.socket(zmq.PUB)
        self.socket_reset.bind("tcp://172.16.0.1:5557")
        self.zmq_params = zmq_params

        

        
        

        ## get some rnti

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Raini - End of zmq inits >>>>>>>>>>>>>>>>>>

        self.observationSize = 2

        lowState = np.zeros(self.observationSize, dtype=np.double)
        highState = np.full(self.observationSize, [
                            self.maxBufferSize, 15], dtype=np.double)

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(
            lowState, highState, dtype=np.double)

    def negotiate_rnti(self):

        print("receiving from mbuff...")
        mbuff_message = self.socket_mbuff.recv()
        self.rnti = int((mbuff_message.split())[0])
        print("...done, got " + str(self.rnti))
        if self.zmq_params == 1:
        
            self.socket_inproc = self.context.socket(zmq.REP)
        
            self.socket_inproc.bind("tcp://*:5559")
            their_rnti = int(self.socket_inproc.recv())
            self.socket_inproc.send_string("")
            while True:
                if their_rnti != self.rnti:
                    print("negotiated " + str(their_rnti) + " for UE1")
                    print("negotiated " + str(self.rnti) + " for UE2")
                    break
                mbuff_message = self.socket_mbuff.recv()
                self.rnti = int((mbuff_message.split())[0])
        else:
            self.socket_inproc = self.context.socket(zmq.REQ)
            self.socket_inproc.connect("tcp://localhost:5559")
            self.socket_inproc.send_string(str(self.rnti))
            self.socket_inproc.recv()

    # def _findStateIndex(self, state):

    #     stateLocation = np.where((self.stateArray == state).all(axis=1))[0][0]
    #     return stateLocation

    def get_state(self):
        #ZMQ sub
        string_mbuff = ""
        string = ""
        print("mark1")
        try:

            # Every 1ms  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - recieve info from RAN (blocking)
            print("d1")
            string = self.socket_get_state.recv()
            print("d1 x")
            # print(string)
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - recieve info from UE client (non-blocking)
            self.socket_mbuff.setsockopt_string(zmq.SUBSCRIBE, str(self.rnti))
            string_mbuff = self.socket_mbuff.recv(flags=zmq.NOBLOCK)
            # print("Raju")
            # print(string_mbuff)
            #string_mbuff = self.socket_mbuff.recv()

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                traceback.print_exec()

        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        messagedata = string.split()  # [ rnti,cqi, ]
        messagedata_buff = string_mbuff.split()  # [ rnti , MB]
        print("mark1 crossed")
        # self.episodeTime = 0
        CQI = self.arm[0][1]
        MB = self.arm[0][0]
        if len(messagedata) > 0:
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract CQI
            CQI = int(messagedata[1])
            self.rnti = int(messagedata[0])

        if len(messagedata_buff) > 0:
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - extract MB
            MB = int(messagedata_buff[1])
        # print(CQI,"<-CQI"+20*"-")
        # print(MB,"<-MB"+20*"-")

        return CQI, MB

    def _calReward(self, media_buffer, action):
        ''' function to calculate next state, and reward given the action'''

        if media_buffer <= 0.1*self.maxBufferSize:  # TODO ask Woo-Hyun to make UDP_client.py implement a fixed maxBufferSize and so that I can set this variable accordingly
            reward = 0
        else:
            reward = 1

        reward = reward - self.cost*action
        return reward

    # def _normalizeState(self, state):
    #     ''' Function for normalizing the remaining load against the max load value'''
    #     state[0] = state[0] / self.maxBufferSize
    #     state[1] = state[1] / 15.0
    #     return state

    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)
        assert action in [0, 1]
        # self.time += 1
        self.episodeTime += 1
        # if self.start:
        #     print("time between steps = ", time.time() - self.start)
        # self.start = time.time()

        # nextState, reward = self._calReward(action)

        #PUB action
        # action = 1
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - sending action to ran. action=1 corresponds to requesting high_rb for this UE (and 0 low_RB)
        str_to_send = str(self.rnti) + " " + str(action)
        self.socket_send_action.send_string(str_to_send)

        done = self.episodeTime == self.episodeLimit

        # get next state
        CQI, MB = self.get_state()
        # while MB == -1:
        #     CQI,MB = self.get_state()
        self.arm[0][1] = CQI
        self.arm[0][0] = MB
        nextState = np.array([MB, CQI], dtype=np.double)
        # nextState = self._normalizeState(nextState)

        # if done:
        reward = self._calReward(MB, action)

        info = {}
        done = False
        return nextState, reward, done, info

    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''
        print("reset reached")
        # self.start = None
        CQI, MB = self.get_state()
        print("crossed")
        # while MB == -1:
        #     CQI,MB = self.get_state()
        self.arm[0][1] = CQI
        self.arm[0][0] = MB
        if self.miniBatchCounter % self.batchSize == 0:

            self.miniBatchCounter = 0

        initialState = np.array(
            [self.arm[0][0], self.arm[0][1]], dtype=np.double)
        # initialState = self._normalizeState(initialState)

        self.miniBatchCounter += 1

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - send reset signal so that udp_client can reset its MB length (to ideally a random value between 10% and 20% max MB capacity)
        self.socket_reset.send_string(str(self.rnti) + " reset")

        return initialState

############################################################################
