import numpy as np
import pandas as pd
import torch
import gym
from gym.spaces import MultiDiscrete, Box, Discrete
from stream_rl.registry import register_env, create_reward
from ray.rllib.env.env_context import EnvContext
from collections import deque
import random


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
        self.total_rbgs = config["num_RBGs"]
        self.cqi_map = config["cqi_map"]

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
        self.cqi_traces_df = pd.read_csv(config["cqi_trace"])
        self.cqi_traces = [
            self.cqi_traces_df.iloc[:, ue].tolist() for ue in range(self.num_UEs)
        ]
        self.cqi_timesteps = [None] * self.num_UEs

        # Action and Observation Space Definitions
        self.action_space = Box(
            low=0.0, high=1.0, shape=(self.num_UEs,), dtype=np.float32
        )
        self.observation_space = Box(
            low=np.array([0, 0] * self.num_UEs),
            high=np.array([self.max_len_backlog, 15] * self.num_UEs),
            dtype=np.float32,
        )

        self.reward_func = create_reward(config["reward"])

    def reset(self):
        self.t = 0
        self.backlog_lens = [0] * self.num_UEs
        self.cqi_timesteps = [
            random.randint(0, len(self.cqi_traces[ue]) - 1)
            for ue in range(self.num_UEs)
        ]
        self.cqis = [
            self.cqi_traces[ue][self.cqi_timesteps[ue]] for ue in range(self.num_UEs)
        ]
        init_state = np.array(
            [
                param[ue]
                for ue in range(self.num_UEs)
                for param in (self.backlog_lens, self.cqis)
            ],
            dtype=np.float32,
        )  # [BL1, CQI1, BL2, CQI2,.....]
        return init_state

    def step(self, action):
        """Order of operations within a step - transfers from :
        1.) Cloud to backlog buffer
        2.) Backlog buffer to playback buffer
        """
        action = np.clip(action, a_min=0.0, a_max=1.0)
        assert (
            action[0] <= 1 and action[0] >= 0 and action[1] <= 1 and action[1] >= 0
        ), f"invalid action : {action}"
        action = list(action)
        action[0] += 0.00000001  # add epsilon to prevent divide by zero
        action[1] += 0.00000001  # add epsilon to prevent divide by zero
        action = tuple(action)
        # Update time
        self.t += 1
        # Update CQI for all UEs according to trace
        total_bytes_transferred = 0
        for ue in range(self.num_UEs):
            self.cqi_timesteps[ue] += 1
            self.cqi_timesteps[ue] %= len(self.cqi_traces[ue])
            self.cqis[ue] = self.cqi_traces[ue][self.cqi_timesteps[ue]]

            # Update BLs
            prob_new_chunk, chunk_size = self.backlog_population_params[ue]
            if np.random.random() < prob_new_chunk:
                self.backlog_lens[ue] += chunk_size
                self.backlog_lens[ue] = min(self.backlog_lens[ue], self.max_len_backlog)

            # Compute RBGs allocated for this UE
            percentage_RBG = action[ue] / sum(action)
            allocated_RBG = int(percentage_RBG * self.total_rbgs)

            # Transfer data from BL to UE
            mean, std = self.cqi_map[self.cqis[ue]]
            bytes_transferred = (
                allocated_RBG
                * np.random.normal(mean, std)
                * np.random.binomial(1, 0.9)  # BLER 10%
                * 1000
            ) // 8
            bytes_transferred = min(bytes_transferred, self.backlog_lens[ue])
            total_bytes_transferred += bytes_transferred
            self.backlog_lens[ue] -= bytes_transferred

        reward = self.reward_func(total_bytes_transferred, self.backlog_lens)

        next_state = np.array(
            [
                param[ue]
                for ue in range(self.num_UEs)
                for param in (self.backlog_lens, self.cqis)
            ],
            dtype=np.float32,
        )  # [BL1, CQI1, BL2, CQI2,.....]

        done = self.t == self.T
        info = {}
        return next_state, reward, done, info
