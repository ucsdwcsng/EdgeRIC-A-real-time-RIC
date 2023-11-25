
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
import time
import random
import datetime 
import numpy as np
import pandas as pd
from gym import spaces
# from numpy.random import RandomState
# from torch import arange
#from stable_baselines.common.env_checker import check_env #this test throws errors and needs tensorflow 1.x with python 3.6. it's normal

class downLinkEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize , episodeLimit, fixedSizeMDP, noiseVar, cost):

        super(downLinkEnv, self).__init__()
        self.noob = True
        self.seed = seed
        self.cost = cost
        # self.myRandomPRNG = random.Random(self.seed)
        self.G = np.random.RandomState(self.seed) # create a special PRNG for a class instantiation
        
        
        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0 
        self.currentEpisode = 0  
        self.noiseVar = noiseVar
        self.classVal = -2

        self.rate = r1
        self.maxBufferSize = maxBufferSize
        self.high_RB = high_RB
        self.low_RB = low_RB
        self.arm = {0:[1, 1]} # [Media buffer, CQI] 

        self.train = Training
        self.batchSize = batchSize
        self.miniBatchCounter = 0
        self.episodeLimit = episodeLimit
        self.fixedSizeMDP = fixedSizeMDP

        

        self.observationSize = 2 

        lowState = np.zeros(self.observationSize, dtype=np.double)
        highState = np.full(self.observationSize, [self.maxBufferSize,15], dtype=np.double)

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(lowState, highState, dtype=np.double)
        self.CQI_range = range(1,16)
        self.CQI_timer = 10

        # Assuming inter frames are 20% the size of key frames and a GoP size of 15 we get
        self.key_frame_size = self.rate / (1/15+14*0.2/15)
        self.inter_frame_size = 0.2*self.key_frame_size
        self.packet_size_mapping = {
            1 : 0.1523,
            2 : 0.2344,
            3 : 0.3770,
            4 : 0.6016,
            5 : 0.8770,
            6 : 1.1758,
            7 : 1.4766,
            8 : 1.9141,
            9 : 2.4063,
            10 : 2.7305,
            11 : 3.3223,
            12 : 3.9023,
            13 : 4.5234,
            14 : 5.1152,
            15 : 5.5547,
            }

    # def _findStateIndex(self, state):
        
    #     stateLocation = np.where((self.stateArray == state).all(axis=1))[0][0]
    #     return stateLocation

    def _calReward(self, action):
        ''' function to calculate next state, and reward given the action'''
        
        CQI = self.arm[0][1]
        assert CQI in range(1,16)
        media_buffer = self.arm[0][0]
        # downlink_buffer = self.arm[0][1]

        

        # Process to generate data at Base Station
        # if self.G.binomial(1,1/15):
        #     bits_generated = self.key_frame_size
        # else:
        #     bits_generated = self.inter_frame_size

        # downlink_buffer += bits_generated
        # downlink_buffer = min(downlink_buffer,self.maxBufferSize)
        
        # Transfer of data between BS and UE
        if action == 1:
            RB = self.high_RB
            
        elif action == 0:
            RB = self.low_RB

        bits_recieved  =   RB*self.packet_size_mapping[CQI]*self.G.binomial(1,0.9)*14*12 #Assuming 90% success rate for transfer
        media_buffer += bits_recieved


        # Process to drain data at UE
        if self.G.binomial(1,1/15):
            bits_drained = self.key_frame_size
        else:
            bits_drained = self.inter_frame_size
        media_buffer -= bits_drained

        media_buffer = min(media_buffer,self.maxBufferSize)
        # downlink_buffer -= bits_recieved

        # Decide reward  
        if media_buffer<=0.1*self.maxBufferSize:
            reward = 0
            media_buffer = 0
        
        else: reward = 1

        self.arm[0][0] = media_buffer
        # self.arm[0][1] = downlink_buffer

        #Decide next CQI
        if self.CQI_timer == 0:
            self.CQI_timer = 10
            CQI = self.G.choice(self.CQI_range)
            self.arm[0][1] = CQI
        nextState = np.array([media_buffer, CQI], dtype=np.double)
        reward = reward - self.cost*action

        return nextState, reward

    # def _normalizeState(self, state):
    #     ''' Function for normalizing the remaining load against the max load value'''
    #     state[0] = state[0] / self.maxBufferSize
    #     state[1] = state[1] / self.maxBufferSize
    #     state[2] = state[2] / 15.0
    #     return state
    
    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)
        assert action in [0,1]
        self.time += 1
        self.CQI_timer -=1
        self.episodeTime += 1
        nextState, reward = self._calReward(action)

        done = self.episodeTime == self.episodeLimit
        # if self.train:
        #     done = bool((nextState[0] == 0)) or (self.episodeTime == self.episodeLimit)
        #     if self.fixedSizeMDP: 
        #         done = False
        #         if nextState[0] == 0:
        #             reward = 0
        # else:
        #     done = bool((nextState[0] == 0))
        
        # nextState = self._normalizeState(nextState)

        if done:
            self.currentEpisode += 1
            self.episodeTime = 0
            if self.train == False:
                self.currentEpisode = 0

        info = {}
        return nextState, reward, done, info 

    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''
        CQI = self.G.choice(self.CQI_range)
        self.CQI_timer = 10
        if self.noob:
            self.noob = False
            low_avg = 0
            high_avg = 0
            count = 0
            for cqi in self.CQI_range:
                count += 1
                bits_transfered_low = self.low_RB*self.packet_size_mapping[cqi]*14*12
                bits_transfered_high = self.high_RB*self.packet_size_mapping[cqi]*14*12
                low_avg += bits_transfered_low
                high_avg += bits_transfered_high
            low_avg = low_avg/count
            high_avg = high_avg/count
            print(
                f"Env stats:\n\tGeneration and draining - {self.rate}\n\t Transfer low action - {0.9*low_avg}\n\t Transfer high action - {0.9*high_avg}"
            )
            # a=input("Ok?")
        self.arm[0][1] = CQI
        # self.arm[0][1] = self.G.choice(range(int(0.1*self.maxBufferSize),int(0.2*self.maxBufferSize)))# Downlink Buffer removed
        self.arm[0][0] = self.G.choice(range(int(0.1*self.maxBufferSize),int(0.2*self.maxBufferSize)))
        if self.miniBatchCounter % self.batchSize == 0:

            self.miniBatchCounter = 0
            
        initialState = np.array([self.arm[0][0], self.arm[0][1], ], dtype=np.double)
        # initialState = self._normalizeState(initialState)

        self.miniBatchCounter += 1
        return initialState

############################################################################
