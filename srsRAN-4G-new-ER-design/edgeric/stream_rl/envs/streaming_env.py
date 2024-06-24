import numpy as np
import gym
from gym.spaces import MultiDiscrete, Box
from stream_rl.registry import register_env, create_reward
from ray.rllib.env.env_context import EnvContext
from collections import deque


@register_env("StreamingEnv")
class StreamingEnv(gym.Env):
    """Straming Env: For the coordinator agent to control"""

    def __init__(self, config: EnvContext):
        self.res_map = config["res_map"]
        self.chunk_map = config["chunk_map"]

        # Playback Buffer Elements
        self.max_len_playback = int(config["media_app"]["max_len"])
        self.max_stall = int(config["media_app"]["max_stall"])
        self.playback_len = None
        self.stall_count = None
        self.playback_buffer = deque()
        self.no_playout = None

        self.prob_new_chunk = config["prob_new_chunk"]
        self.prob_playout = config["prob_playout"]
        self.prob_reset = config["prob_reset"]

        # Backlog Buffer Elements
        self.channel_probs = list(config["base_station"]["channel_probs"])
        self.max_len_backlog = int(config["base_station"]["max_len"])
        self.backlog_len = None
        self.backlog_buffer = deque()

        # Action and Observation Space Definitions
        num_resolutions = len(self.chunk_map)
        num_channels = len(self.channel_probs)
        self.action_space = MultiDiscrete(
            [num_channels, num_resolutions, num_resolutions + 1]
        )  # [Backlog action, Cloud action, Playout action]
        self.observation_space = Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)

        self.reward_func = create_reward(config["reward"])

    def reset(self):
        self.backlog_buffer = deque()
        self.playback_buffer = deque()
        self.playback_len = 0.0
        self.stall_count = 0.0
        self.backlog_len = 0.0
        self.no_playout = False
        init_state = np.array(
            [
                self.backlog_len / self.max_len_backlog,
                self.playback_len / self.max_len_playback,
                self.stall_count / self.max_stall,
            ],
            dtype=np.float32,
        )
        return init_state

    def step(self, action):
        """Order of operations within a step - transfers from :
        1.) Cloud to backlog buffer
        2.) Backlog buffer to playback buffer
        3.) Playout from playback buffer"""

        # 1) Cloud to Backlog
        random_number = np.random.random()
        if random_number < self.prob_new_chunk:  # Bernoulli success for new chunk
            free_space_backlog = self.max_len_backlog - self.backlog_len
            chunk = list(self.chunk_map.keys())[
                action[1]
            ]  # Map action to chunk-resolution
            if self.chunk_map[chunk] <= free_space_backlog:
                self.backlog_buffer.append(chunk)
                self.backlog_len += self.chunk_map[chunk]

        # 2) Backlog to Playback
        random_number = np.random.random()
        if (
            random_number < self.channel_probs[action[0]]
            and len(self.backlog_buffer) > 0
        ):  # Bernoulli success for channel and backlog buffer has chunks
            free_space_playback = self.max_len_playback - self.playback_len
            chunk = self.backlog_buffer[0]
            if self.res_map[chunk] <= free_space_playback:
                chunk = self.backlog_buffer.popleft()
                self.backlog_len -= self.res_map[chunk]
                self.playback_buffer.append(chunk)
                self.playback_len += self.res_map[chunk]

        # 3) Playout
        random_number = np.random.random()
        if action[2]:  # Try and playout one chunk
            if (
                random_number < self.prob_playout and len(self.playback_buffer) > 0
            ):  # Bernoulli success for playout and playback buffer has chunks
                num_chunks = list(self.chunk_map.keys())[action[2] - 1]
                for _ in num_chunks:
                    chunk = self.playback_buffer.popleft()
                    self.playback_len -= self.chunk_map[chunk]
                self.no_playout = False
            else:  # No playout due to bernouilli failure or dry buffer
                if not self.no_playout:
                    self.stall_count += 1  # Not a contniued stall
                self.no_playout = True
        else:  # No playout due to choice of action
            if not self.no_playout:
                self.stall_count += 1  # Not a contniued stall
            self.no_playout = True
        self.stall_count = min(self.stall_count, self.max_stall)

        # Reset media app with small prob
        random_number = np.random.random()
        if random_number < self.prob_reset:
            done = True
        else:
            done = False

        next_state = np.array(
            [
                self.backlog_len / self.max_len_backlog,
                self.playback_len / self.max_len_playback,
                self.stall_count / self.max_stall,
            ],
            dtype=np.float32,
        )

        reward = self.reward_func()  # TODO
        info = {}
        return next_state, reward, done, info
