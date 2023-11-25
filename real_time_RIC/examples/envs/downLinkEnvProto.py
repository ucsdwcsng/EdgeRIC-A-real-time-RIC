
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

class downLinkEnvProto(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize , episodeLimit, fixedSizeMDP, noiseVar, cost):

        super(downLinkEnvProto, self).__init__()
        self.seed = seed
        self.cost = cost
        # self.myRandomPRNG = random.Random(self.seed)
        self.G = np.random.RandomState(self.seed) # create a special PRNG for a class instantiation
        self.classVal = -1
        
        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0 
        self.currentEpisode = 0  
        self.noiseVar = noiseVar

        self.rate = r1
        self.maxBufferSize = maxBufferSize #500
        # self.high_RB = high_RB
        # self.low_RB = low_RB
        self.arm = {0:[1,1]} # [Media buffer,CQI] 

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

    # def _findStateIndex(self, state):
        
    #     stateLocation = np.where((self.stateArray == state).all(axis=1))[0][0]
    #     return stateLocation

    def _calReward(self, action):
        ''' function to calculate next state, and reward given the action'''
        # packet_size_mapping = {
        #     1 : 0.1523,
        #     2 : 0.2344,
        #     3 : 0.3770,
        #     4 : 0.6016,
        #     5 : 0.8770,
        #     6 : 1.1758,
        #     7 : 1.4766,
        #     8 : 1.9141,
        #     9 : 2.4063,
        #     10 : 2.7305,
        #     11 : 3.3223,
        #     12 : 3.9023,
        #     13 : 4.5234,
        #     14 : 5.1152,
        #     15 : 5.5547,
        #     }
        CQI = self.arm[0][1]
        assert CQI in [14,15]
        media_buffer = self.arm[0][0]
        downlink_buffer = self.maxBufferSize

        bytes_drained = self.rate

        media_buffer -= bytes_drained

        

        
        # Transfer of data between BS and UE
        if action == 1 and CQI==14:
            bytes_recieved  =  1.2*self.rate
            
        elif action == 0 and CQI==14:
            bytes_recieved  =  0.8*self.rate
        elif action == 1 and CQI==15:
            bytes_recieved  =  1.4*self.rate
            
        elif action == 0 and CQI==15:
            bytes_recieved  =  1.0*self.rate

        
        media_buffer += bytes_recieved

        # Decide reward  
        if media_buffer<=0:
            reward = 0
            media_buffer = 0
        else: reward = 1
        self.arm[0][0] = media_buffer
        self.arm[0][1] = CQI
        nextState = np.array([media_buffer,CQI], dtype=np.double)
        reward = reward - self.cost*action
        return nextState, reward

    # def _normalizeState(self, state):
    #     ''' Function for normalizing the remaining load against the max load value'''
    #     state[0] = state[0] / self.maxBufferSize
    #     state[1] = state[1] / 15.0
    #     return state
    
    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        assert self.action_space.contains(action)
        assert action in [0,1]
        self.time += 1
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
            # self.episodeTime = 0
            if self.train == False:
                self.currentEpisode = 0

        info = {}
        return nextState, reward, done, info 

    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''

        self.episodeTime = 0
        CQI = self.G.choice([14,15])
        # print(CQI)
        self.arm[0][1] = CQI
        self.arm[0][0] = 1.5*self.rate#self.G.choice(range(int(0.3*self.maxBufferSize)))
        if self.miniBatchCounter % self.batchSize == 0:

            self.miniBatchCounter = 0
            
        initialState = np.array([self.arm[0][0],self.arm[0][1] ], dtype=np.double)
        # initialState = self._normalizeState(initialState)

        self.miniBatchCounter += 1
        return initialState

############################################################################
