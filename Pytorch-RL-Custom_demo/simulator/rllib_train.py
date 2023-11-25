from pprint import pprint
import numpy as np
import hydra
import time
import torch

# Import the RL algorithm (Trainer) we would like to use.
from ray.rllib.algorithms.registry import ALGORITHMS

from stream_rl.callbacks import BaselineAgentsCallbacks
from stream_rl.registry import ENVS
from stream_rl.plots import visualize_policy, visualize_edgeric
import debugpy

debugpy.listen(5678)
print("waiting to attach")
debugpy.wait_for_client()
print("attached")
num_workers = 0

# Configure the algorithm.
ray_config = {
    # Environment (RLlib understands openAI gym registered strings).
    # "env": GvaeEnv,
    "env_config": {},
    # Use 2 environment workers (aka "rollout workers") that parallelly
    # collect samples from their own environment clone(s).
    "num_gpus": 0,  # TODO, figure out scaling up to num_gpus,
    # "num_gpus_per_worker": num_gpus_per_worker,
    "num_workers": num_workers,
    # "callbacks": BaselineAgentsCallbacks,
    # "num_"
    # Change this to "framework: torch", if you are using PyTorch.
    # Also, use "framework: tf2" for tf2.x eager execution.
    "framework": "torch",
    # Tweak the default model provided automatically by RLlib,
    # given the environment's observation- and action spaces.
    "model": {"fcnet_hiddens": [64, 64], "_disable_preprocessor_api": False},
    # Set up a separate evaluation worker set for the
    # `trainer.evaluate()` call after training (see below).
    # "evaluation_interval": 10,
    # "evaluation_duration": 196,
    # Only for evaluation runs, render the env.
    "evaluation_config": {
        "render_env": False,
        "explore": False,
    },
    ##Make stuff divisible by 7
    "train_batch_size": 196,
    "rollout_fragment_length": 196,
    # More verbode
    # "log_level": "INFO",
}


class MaxCQIAgent:
    def __init__(self) -> None:
        pass

    def restore(self, arg1):
        pass

    def compute_single_action(self, obs):
        cqis = obs[1::2]
        return np.eye(len(cqis))[np.argmax(cqis)]


class MaxBacklogAgent:
    def __init__(self) -> None:
        pass

    def restore(self, arg1):
        pass

    def compute_single_action(self, obs):
        backlog_lens = obs[::2]
        return np.eye(len(backlog_lens))[np.argmax(backlog_lens)]


def value_iteration(env_cls, env_config, convergence_tolerance):
    env = env_cls(env_config)
    print()
    # 1. Initialize V and Q tables
    V = np.zeros(env.observation_space.nvec)
    Q = np.zeros(np.append(env.observation_space.nvec, env.action_space.nvec))

    # 2. Perform bellman backup until convergence
    iter = 0
    while True:
        delta = 0

        # 2.1 Loop through each state
        for s in env.all_states:
            # 2.1.1 Archive old state value
            v = V[s]

            # 2.1.2 New state value = max of q-value
            Q[s] = q_value(env, V, s)
            V[s] = np.max(Q[s])

            delta = max(delta, abs(V[s] - v))

        print(f"iter: {iter}\n delta:{delta}\n\n")
        iter += 1
        # 2.2 If state value changes small, converged
        if delta < convergence_tolerance:
            break

    Pi = np.zeros(np.append(env.observation_space.nvec, env.action_space.nvec))
    # Populate one-hot encoded Pi Visualize Results TODO better!!
    for s in env.all_states:
        Pi[s][np.unravel_index(np.argmax(Q[s]), Q[s].shape)] = 1

    visualize_policy(Pi)


def q_value(env, V, s):
    q = np.zeros(env.action_space.nvec)
    for a in env.all_actions:
        reward, possible_transitions = env.P[s][a]
        for prob, next_state in possible_transitions:
            q[a] += prob * (reward + env.gamma * V[next_state])
    return q


@hydra.main(config_path="conf", config_name="example", version_base=None)
def main(conf):
    # TODO: de-spaghetti
    ray_config["env"] = ENVS[conf["env"]]
    ray_config["env_config"].update(conf["env_config"])
    # ray_config["evaluation_config"]["env_config"].update(conf["env_config"])

    # For VI
    if conf["algorithm"] == "VI":
        value_iteration(
            ray_config["env"],
            conf["env_config"],
            conf["algorithm_params"]["convergence_tolerance"],
        )
    else:
        # Create our RLlib Trainer.
        trainer_cls, _ = ALGORITHMS[conf["algorithm"]]()

        trainer = trainer_cls(config=ray_config)
        # TODO DDPG, SAC support

        train_rewards = []
        for train_step in range(10):
            results_dict = trainer.train()
            print(train_step, "+" * 80)
            print("Max:", results_dict["episode_reward_max"])
            print("Average:", results_dict["episode_reward_mean"])
            train_rewards.append(results_dict["episode_reward_mean"])
            if (train_step + 1) % 10 == 0:
                checkpoint_path = trainer.save()

    trainer.export_policy_model(".")

    # Evaluate the trained agent against baselines

    max_cqi_agent = MaxCQIAgent()
    max_backlog_agent = MaxBacklogAgent()
    ppo_agent_rewards = evaluate_agent(
        ENVS[conf["env"]], conf["env_config"], trainer, checkpoint_path
    )
    cqi_agent_rewards = evaluate_agent(
        ENVS[conf["env"]], conf["env_config"], max_cqi_agent, checkpoint_path
    )
    backlog_agent_rewards = evaluate_agent(
        ENVS[conf["env"]], conf["env_config"], max_backlog_agent, checkpoint_path
    )

    # plot
    visualize_edgeric(
        train_rewards, ppo_agent_rewards, cqi_agent_rewards, backlog_agent_rewards
    )


def evaluate_agent(env_class, env_config, agent, checkpoint_path):
    # instantiate env class
    env_config.update({"seed": 10})
    env = env_class(env_config)
    agent.restore(checkpoint_path)
    num_episodes = 10
    episode_rewards = []
    for episode in range(num_episodes):

        # run until episode ends

        episode_reward = 0
        done = False
        obs = env.reset()
        while not done:
            start = time.time()
            with torch.no_grad():
                action = agent.compute_single_action(obs)
            print(time.time() - start)
            a = input("some")
            print("obs-", obs, "action-", action)
            a = input("Raju")
            obs, reward, done, info = env.step(action)
            episode_reward += reward
        episode_rewards.append(episode_reward)
    return episode_rewards


if __name__ == "__main__":
    main()