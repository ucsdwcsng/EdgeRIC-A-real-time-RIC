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
        self.stall = 0
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
        self.mbs =[]
   
        self.action_space = Box(
            low=0.0, high=1.0, shape=(self.num_UEs,), dtype=np.float32
        )
        self.observation_space = Box(
            low=np.array([0, 0, 0] * self.num_UEs),
            high=np.array([self.max_len_backlog, 15, 6000000] * self.num_UEs),
            dtype=np.float32,
        )
       
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

    def reset(self):
        self.t = 0
        self.stall = 0
        
        self.backlog_lens = [0] * self.num_UEs
        self.cqis = [1] * self.num_UEs
        self.mbs = [3000000]*self.num_UEs
      
        if self.augment_state_space:
            
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
        
        action = np.clip(
            action, a_min=0.00000001, a_max=1.0
        )  # Project action back to action space + add epsilon to prevent divide by zero error

        # Add delay to action
        self.action_history.append(action)
        action = self.action_history[0]

        # Update time
        self.t += 1
        
        total_bytes_transferred = 0
        num_ues = len(RNTIs)
        #print(f"size of mbs: {RNTIs}")
        
        for ue in range(num_ues): 
            
            self.mbs[ue] = MBs[ue]
            self.cqis[ue] = CQIs[ue]
            
            # Update BLs
            inter_arrival_time, chunk_size = self.backlog_population_params[ue]
            self.backlog_lens[ue] = BLs[ue]

        #reward = self.reward_func(total_bytes_transferred, self.backlog_lens)
        reward = self.reward_func(tx_bytes, self.backlog_lens, self.stall)
      
        self.stall = 0
        if self.augment_state_space:
            self.back_pressures = [
                cqi * backlog_len
                for cqi, backlog_len in zip(self.cqis, self.backlog_lens)
            ]
            next_state = np.array(
                [
                    param[ue]
                    for ue in range(num_ues)
                    for param in (self.backlog_lens, self.cqis, self.back_pressures)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BP1, BL2, CQI2, BP2,.....]
        else:
            next_state = np.array(
                [
                    param[ue]
                    for ue in range(num_ues)
                    for param in (self.backlog_lens, self.cqis, self.mbs)
                ],
                dtype=np.float32,
            )  # [BL1, CQI1, BL2, CQI2,.....]

        done = self.t == self.T
        info = {}
     
        self.state_history.append(next_state)  # Add delay to state observation
        return self.state_history[0], reward, done, info



    

    
