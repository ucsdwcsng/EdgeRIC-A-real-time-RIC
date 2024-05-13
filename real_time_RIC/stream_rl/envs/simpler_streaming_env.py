import itertools
import numpy as np
import gym
from gym.spaces import MultiDiscrete
from stream_rl.registry import register_env, create_reward
from ray.rllib.env.env_context import EnvContext


@register_env("SimplerStreamingEnv")
class SimplerStreamingEnv(gym.Env):
    """Straming Env: Simpler model, to verify Nouman's results empirically"""

    def __init__(self, config: EnvContext):

        self.T = config["T"]
        self.gamma = config["discount_factor"]

        # Backlog buffer population process
        self.prob_new_chunk = config["prob_new_chunk"]

        # Playback Buffer Elements
        self.playout_probs = list(config["media_app"]["channel_probs"])
        self.max_len_playback = int(config["media_app"]["max_len"])
        self.playback_len = None

        # Backlog Buffer Elements
        self.channel_probs = list(config["base_station"]["channel_probs"])
        self.max_len_backlog = int(config["base_station"]["max_len"])
        self.backlog_len = None

        # Action and Observation Space Definitions
        num_playout_probs = len(self.playout_probs)
        num_channel_probs = len(self.channel_probs)
        self.action_space = MultiDiscrete(
            [num_channel_probs, num_playout_probs]
        )  # [Backlog action (V_t), Playout action (U_t)]
        self.observation_space = MultiDiscrete(
            [
                self.max_len_backlog + 1,
                self.max_len_playback + 1,
            ]
        )  # [X_{t},Y_{t}]

        self.reward_func = create_reward(config["reward"])
        self.cost_params = config["cost_params"]

        # Data Structures for Model-based Learning
        self.all_actions = [
            action
            for action in itertools.product(*[range(n) for n in self.action_space.nvec])
        ]
        self.all_states = [
            state
            for state in itertools.product(
                *[range(n) for n in self.observation_space.nvec]
            )
        ]
        self.P = {
            s: {
                a: (
                    self.reward_func(
                        self.playout_probs[a[1]], s[1], a[0], self.cost_params
                    ),  # beta_Ut , Y_t, V_t, cost_params
                    self._compute_transitions(s, a),
                )
                for a in self.all_actions
            }
            for s in self.all_states
        }

    def _compute_transitions(self, state, action):
        possible_transitions = []
        backlog_len, playback_len = state
        backlog_action, playout_action = action

        free_space_playback = self.max_len_playback - playback_len
        free_space_backlog = self.max_len_backlog - backlog_len

        if free_space_playback == 0:
            if free_space_backlog == 0:
                possible_transitions.append(
                    (
                        self.playout_probs[playout_action],
                        [backlog_len, playback_len - 1],
                    )
                )
                possible_transitions.append(
                    (
                        1 - self.playout_probs[playout_action],
                        [backlog_len, playback_len],
                    )
                )
            else:
                possible_transitions.append(
                    (
                        self.playout_probs[playout_action] * (1 - self.prob_new_chunk),
                        [backlog_len, playback_len - 1],
                    )
                )
                possible_transitions.append(
                    (
                        self.playout_probs[playout_action] * self.prob_new_chunk,
                        [backlog_len + 1, playback_len - 1],
                    )
                )
                possible_transitions.append(
                    (
                        (1 - self.playout_probs[playout_action])
                        * (1 - self.prob_new_chunk),
                        [backlog_len, playback_len],
                    )
                )
                possible_transitions.append(
                    (
                        (1 - self.playout_probs[playout_action]) * self.prob_new_chunk,
                        [backlog_len + 1, playback_len],
                    )
                )
        else:
            if free_space_backlog == 0:
                possible_transitions.append(
                    (
                        self.playout_probs[playout_action]
                        * self.channel_probs[backlog_action],
                        [backlog_len - 1, playback_len - 1],
                    )
                )

    def reset(self):
        self.t = 0
        self.playback_len = 0
        self.backlog_len = 0
        init_state = np.array(
            [
                self.backlog_len,
                self.playback_len,
            ],
            dtype=int,
        )
        return init_state

    def step(self, action):
        """Order of operations within a step - transfers from :
        1.) Cloud to backlog buffer
        2.) Backlog buffer to playback buffer
        3.) Playout from playback buffer"""

        self.t += 1
        reward = self.reward_func(
            self.playout_probs[action[1]],
            self.playback_len,
            action[0],
            self.cost_params,
        )

        # 1) Cloud to Backlog
        random_number = np.random.random()
        if random_number < self.prob_new_chunk:  # Bernoulli success for new chunk
            self.backlog_len += 1
            self.backlog_len = min(self.backlog_len, self.max_len_backlog)

        # 2) Backlog to Playback
        random_number = np.random.random()
        if (
            random_number < self.channel_probs[action[0]]
            and len(self.backlog_buffer) > 0
        ):  # Bernoulli success for channel and backlog buffer has chunks
            free_space_playback = self.max_len_playback - self.playback_len
            if free_space_playback > 0:
                self.backlog_len -= 1
                self.playback_len += 1

        # 3) Playout
        random_number = np.random.random()
        if (
            random_number < self.playout_probs[action[1]]
            and len(self.playback_buffer) > 0
        ):  # Bernoulli success for playout and playback buffer has chunks
            self.playback_len -= 1

        next_state = np.array(
            [
                self.backlog_len,
                self.playback_len,
            ],
            dtype=int,
        )

        done = self.t == self.T
        info = {}
        return next_state, reward, done, info
