'''
Create multiarm env from single arm envs
'''

from collections import defaultdict
from email.policy import default
from typing import DefaultDict
import gym
import itertools
import math
import time
import random
import datetime 
import numpy as np
import pandas as pd
from gym import spaces
from envs.downLinkEnv import downLinkEnv
from envs.downLinkEnvProto import downLinkEnvProto
from envs.downLinkEnvProtoRAN import downLinkEnvProtoRAN
from threading import Thread
# from numpy.random import RandomState
# from torch import arange
#from stable_baselines.common.env_checker import check_env #this test throws errors and needs tensorflow 1.x with python 3.6. it's normal
BATCHSIZE = 5 #Dummy
EPISODELIMIT = 300
numEpisodes = 2000 #Dummy
TRAIN = True
noiseVar = 0.0 #Dummy
SEED = 50

class multiArmWrapper(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed, numEpisodes,  Training, r1,  high_RB, low_RB, maxBufferSize, batchSize , episodeLimit, fixedSizeMDP, noiseVar, singleArmEnvType, numArms, scheduleArms):

        super(multiArmWrapper, self).__init__()
        self.seed = seed
        self.singleArmEnvType = singleArmEnvType
        self.scheduleArms = scheduleArms
        # self.myRandomPRNG = random.Random(self.seed)
        self.G = np.random.RandomState(self.seed) # create a special PRNG for a class instantiation
        
        self.classVal = -1
        
        self.time = 0
        self.numEpisodes = numEpisodes
        self.episodeTime = 0 
        self.currentEpisode = 0  
        self.noiseVar = noiseVar
        self.numArms = numArms
        self.rate = r1
        self.maxBufferSize = maxBufferSize #500
        self.high_RB = high_RB
        self.low_RB = low_RB
        self.state = []
        self.envs = {}

        self.train = Training
        self.batchSize = batchSize
        self.miniBatchCounter = 0
        self.episodeLimit = episodeLimit
        self.fixedSizeMDP = fixedSizeMDP
        self.envSeeds = self.G.randint(0, 10000, size=self.numArms)
        
        self._createActionTable()
        self.observationSize = self.numArms*2
        maxState = np.tile([self.maxBufferSize, 15.0], self.numArms) #[MB,CQI]
        lowState = np.zeros(self.observationSize, dtype=np.double)
        highState = np.full(self.observationSize, maxState, dtype=np.double) #Actually redundant?

    
        self.observation_space = spaces.Box(lowState, highState, dtype=np.double)

        self._setTheArms()

    def _setTheArms(self):
        ''' function that sets the N arms for training'''

        
        
        # zmq_params = [(UE1_ips_and_ports,),(UE2_ips_and_ports)]  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Raini - Hardcode any info needed for socket inits here
        for i in range(self.numArms):
            if self.singleArmEnvType == "down_link_proto":
                self.envs[i] = downLinkEnvProto(numEpisodes=numEpisodes, seed=self.envSeeds[i], Training=TRAIN, r1=10, high_RB=40,low_RB = 20, maxBufferSize=500, batchSize=BATCHSIZE,
            episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = 0)
            elif self.singleArmEnvType == "down_link":
                self.envs[i] = downLinkEnv(numEpisodes=numEpisodes, seed=self.envSeeds[i], Training=TRAIN, r1=4000, high_RB=12,low_RB = 6, maxBufferSize=75000, batchSize=BATCHSIZE,
            episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = 0) 
            elif self.singleArmEnvType == "down_link_proto_ran":
                self.envs[i] = downLinkEnvProtoRAN(numEpisodes=numEpisodes, seed=SEED, Training=TRAIN, r1=2*517, high_RB=40,low_RB = 20, maxBufferSize=10000, batchSize=BATCHSIZE,
            episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = 0, zmq_params = i) #<< Raini - And the individual arms will recieve them through here
            else: raise NotImplementedError #To implement RAN version, need to sort out passing UE ip adress and port
        if self.singleArmEnvType == "down_link_proto_ran":
            #threading
            workers=[]
            for i in range(self.numArms):
                worker_args = ( SEED, numEpisodes, TRAIN, 2*517, 40,20, 10000, BATCHSIZE,EPISODELIMIT,False,noiseVar, 0, i)
                workers.append(Thread(target=self.envs[i].negotiate_rnti))
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()

    def _createActionTable(self):
        '''function that creates a mapping of actions to take. Will be mapped with the action taken from the agent.'''
        
        self.actionTable  = list(itertools.product([0, 1], repeat=self.numArms))
        self.actionTable = [x for x in self.actionTable if  sum(x) == self.scheduleArms]
        self.action_space = spaces.Discrete(len(self.actionTable))
             

    # def _findStateIndex(self, state):
        
    #     stateLocation = np.where((self.stateArray == state).all(axis=1))[0][0]
    #     return stateLocation

    def _calReward(self, action):
        ''' function to calculate next state, and reward given the action'''
        if self.actionTable != None:
        
            actionVector = self.actionTable[action]
        else:
            raise NotImplementedError
        cumReward = 0
        state = []
        print("please")
        envThreads = []
        for i in range(len(actionVector)):
            
            envThreads.append( Thread(target=self.envs[envCounter].step, args=actionVector[i]) )
        
        for t in envThreads:
            t.start()
        for t in envThreads:
            nextState, reward, done, info = t.join()
            state.append(nextState[0])
            state.append(nextState[1])
            cumReward += reward
            
        

        state = np.array(state, dtype=np.double)

        return state, cumReward

    
    
    def step(self, action):
        ''' Standard Gym function for taking an action. Supplies nextstate, reward, and episode termination signal.'''
        
        self.time += 1
        self.episodeTime += 1

        nextState, reward = self._calReward(action)
        done = bool(self.episodeTime == self.episodeLimit)

        if done: 
            self.currentEpisode += 1
            self.episodeTime = 0

        info = {}
        
        return nextState, reward, done, info

    def reset(self):
        ''' Standard Gym function for supplying initial episode state.'''

        self.state = []
        envThreads = []
        print("here")
        for i in self.envs:
            envThreads.append(Thread(target=self.envs[i].reset))
        for t in envThreads:
            t.start()
        for t in envThreads:
            state = t.join()
            print("--state",state)
            self.state.extend(state)
            
        print("raju")
        self.state = np.array(self.state, dtype=np.double)
        
        return self.state

############################################################################
