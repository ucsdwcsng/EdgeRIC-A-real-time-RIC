import itertools
import numpy as np
import gym
from gym.spaces import MultiDiscrete
from stream_rl.registry import register_env, create_reward
from ray.rllib.env.env_context import EnvContext


@register_env("SingleAgentEnv")
class SingleAgentEnv(gym.Env):
    """Simplified Single Agent Env: Described in <Dheeraj's pdf link>"""  # TODO add link?

    def __init__(self, config: EnvContext):
        self.T = config["T"]
        self.gamma = config["discount_factor"]

        # Edge Device Elements
        self.max_len_playback = int(config["edge_device"]["max_len"])
        self.playback_len = None  # Y_{t}^(n,1)
        self.no_playout_previously = None  # Y_{t}^(n,2)
        num_edge_device_actions = len(config["edge_device"]["U_t"])

        # Base Station Elements
        self.tx_success_prob = config["base_station"]["success_prob"]  # p_{n}
        num_base_station_actions = len(config["base_station"]["V_t"])

        # Action and Observation Space Definitions
        self.action_space = MultiDiscrete(
            [num_base_station_actions, num_edge_device_actions]
        )  # [Backlog action, Playout action]
        self.observation_space = MultiDiscrete(
            [self.max_len_playback + 1, 2]
        )  # [Y_{t}^(n,1),Y_{t}^(n,2)]

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
                        (a[0], min(a[1], s[0])), s[1], self.cost_params
                    ),  # min to restrict the action space
                    self._compute_transitions(s, a),
                )
                for a in self.all_actions
            }
            for s in self.all_states
        }

    def reset(self):
        self.t = 0
        self.playback_len = 0
        self.no_playout_previously = 0
        init_state = np.array(
            [self.playback_len, self.no_playout_previously], dtype=np.int
        )
        return init_state

    def step(self, action):
        self.t += 1
        backlog_action, playout_action = action  # V_t , U_t
        playout_action = min(
            playout_action, self.playback_len
        )  # Restrict action space for low playback_len
        action = (backlog_action, playout_action)
        # Playout
        self.playback_len -= playout_action
        self.playback_len = max(0, self.playback_len)

        # TX : base_station -> edge_device
        random_number = np.random.random()
        if random_number < self.tx_success_prob:
            free_space = self.max_len_playback - self.playback_len
            if backlog_action <= free_space:
                self.playback_len += backlog_action

        reward = self.reward_func(action, self.no_playout_previously, self.cost_params)

        self.no_playout_previously = 1 if not playout_action else 0

        next_state = np.array(
            [self.playback_len, self.no_playout_previously], dtype=np.int
        )

        info = {}
        done = self.t == self.T
        return next_state, reward, done, info

    def _compute_transitions(self, state, action):
        possible_transitions = []
        playback_len, no_playout_prev = state
        backlog_action, playout_action = action
        playout_action = min(playout_action, playback_len)

        no_playout_prev = 1 if not playout_action else 0

        playback_len -= playout_action
        free_space = self.max_len_playback - playback_len
        if backlog_action == 0 or free_space < backlog_action:
            possible_transitions.append((1.0, [playback_len, no_playout_prev]))
        else:
            possible_transitions.append(
                (1 - self.tx_success_prob, [playback_len, no_playout_prev])
            )
            possible_transitions.append(
                (self.tx_success_prob, [playback_len + backlog_action, no_playout_prev])
            )

        return possible_transitions
