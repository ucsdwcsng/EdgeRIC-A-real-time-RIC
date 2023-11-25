import argparse
import hydra
import gym
import os
import sys
import pickle
import time
import debugpy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from models.mlp_policy import Policy
from models.mlp_critic import Value
from models.mlp_policy_disc import DiscretePolicy
from core.ppo import ppo_step
from core.common import estimate_advantages
from core.agent_original import Agent

from stream_rl.registry import ENVS
from stream_rl.plots import visualize_edgeric, plot_cdf

# Code for debugging
# debugpy.listen(5678)
# print("waiting to attach")
# debugpy.wait_for_client()
# print("attached")

parser = argparse.ArgumentParser(description="PyTorch PPO example")
parser.add_argument(
    "--env-name",
    default="Hopper-v2",
    metavar="G",
    help="name of the environment to run",
)
parser.add_argument("--model-path", metavar="G", help="path of pre-trained model")
parser.add_argument(
    "--render", action="store_true", default=False, help="render the environment"
)
parser.add_argument(
    "--log-std",
    type=float,
    default=-0.0,
    metavar="G",
    help="log std for the policy (default: -0.0)",
)
parser.add_argument(
    "--gamma",
    type=float,
    default=0.99,
    metavar="G",
    help="discount factor (default: 0.99)",
)
parser.add_argument(
    "--tau", type=float, default=0.95, metavar="G", help="gae (default: 0.95)"
)
parser.add_argument(
    "--l2-reg",
    type=float,
    default=1e-3,
    metavar="G",
    help="l2 regularization regression (default: 1e-3)",
)
parser.add_argument(
    "--learning-rate",
    type=float,
    default=3e-4,
    metavar="G",
    help="learning rate (default: 3e-4)",
)
parser.add_argument(
    "--clip-epsilon",
    type=float,
    default=0.2,
    metavar="N",
    help="clipping epsilon for PPO",
)
parser.add_argument(
    "--num-threads",
    type=int,
    default=1,
    metavar="N",
    help="number of threads for agent (default: 4)",
)
parser.add_argument(
    "--seed", type=int, default=1, metavar="N", help="random seed (default: 1)"
)
parser.add_argument(
    "--min-batch-size",
    type=int,
    default=2048,
    metavar="N",
    help="minimal batch size per PPO update (default: 2048)",
)
parser.add_argument(
    "--eval-batch-size",
    type=int,
    default=2048,
    metavar="N",
    help="minimal batch size for evaluation (default: 2048)",
)
parser.add_argument(
    "--max-iter-num",
    type=int,
    default=100,
    metavar="N",
    help="maximal number of main iterations (default: 500)",
)
parser.add_argument(
    "--log-interval",
    type=int,
    default=1,
    metavar="N",
    help="interval between training status logs (default: 10)",
)
parser.add_argument(
    "--save-model-interval",
    type=int,
    default=0,
    metavar="N",
    help="interval between saving model (default: 0, means don't save)",
)
parser.add_argument("--gpu-index", type=int, default=0, metavar="N")
args = parser.parse_args()


class MaxCQIAgent:
    def __init__(self) -> None:
        pass

    def restore(self, arg1):
        pass

    def select_action(self, obs):
        cqis = obs[1::2]
        return np.eye(len(cqis))[np.argmax(cqis)]


class MaxPressureAgent:
    def __init__(self) -> None:
        pass

    def restore(self, arg1):
        pass

    def select_action(self, obs):
        backlog_lens = obs[::2]
        cqis = obs[1::2]
        pressure = [b * c for b, c in zip(backlog_lens, cqis)]
        return np.eye(len(backlog_lens))[np.argmax(pressure)]


@hydra.main(config_path="conf", config_name="edge_ric", version_base=None)
def main(conf):
    dtype = torch.float32
    torch.set_default_dtype(dtype)
    device = (
        torch.device("cuda", index=args.gpu_index)
        if torch.cuda.is_available()
        else torch.device("cpu")
    )
    if torch.cuda.is_available():
        torch.cuda.set_device(args.gpu_index)

    """environment"""
    env_cls = ENVS[conf["env"]]
    env = env_cls(conf["env_config"])
    state_dim = env.observation_space.shape[0]
    is_disc_action = len(env.action_space.shape) == 0
    running_state = None
    # running_state = ZFilter((state_dim,), clip=5)
    # running_reward = ZFilter((1,), demean=False, clip=10)

    """seeding"""
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    # env.seed(args.seed)

    """define actor and critic"""
    if args.model_path is None:
        if is_disc_action:
            policy_net = DiscretePolicy(state_dim, env.action_space.n)
        else:
            policy_net = Policy(
                state_dim,
                env.action_space.shape[0],
                log_std=args.log_std,
                activation="sigmoid",
            )
        value_net = Value(state_dim)
    else:
        policy_net, value_net, running_state = pickle.load(open(args.model_path, "rb"))
    policy_net.to(device)
    value_net.to(device)

    optimizer_policy = torch.optim.Adam(policy_net.parameters(), lr=args.learning_rate)
    optimizer_value = torch.optim.Adam(value_net.parameters(), lr=args.learning_rate)

    # optimization epoch number and batch size for PPO
    optim_epochs = 10
    optim_batch_size = 64

    """create agent"""
    agent = Agent(
        env,
        policy_net,
        device,
        running_state=running_state,
        num_threads=args.num_threads,
    )

    def update_params(batch, i_iter):
        states = torch.from_numpy(np.stack(batch.state)).to(dtype).to(device)
        actions = torch.from_numpy(np.stack(batch.action)).to(dtype).to(device)
        rewards = torch.from_numpy(np.stack(batch.reward)).to(dtype).to(device)
        masks = torch.from_numpy(np.stack(batch.mask)).to(dtype).to(device)
        with torch.no_grad():
            values = value_net(states)
            fixed_log_probs = policy_net.get_log_prob(states, actions)

        """get advantage estimation from the trajectories"""
        advantages, returns = estimate_advantages(
            rewards, masks, values, args.gamma, args.tau, device
        )

        """perform mini-batch PPO update"""
        optim_iter_num = int(math.ceil(states.shape[0] / optim_batch_size))
        for _ in range(optim_epochs):
            perm = np.arange(states.shape[0])
            np.random.shuffle(perm)
            perm = LongTensor(perm).to(device)

            states, actions, returns, advantages, fixed_log_probs = (
                states[perm].clone(),
                actions[perm].clone(),
                returns[perm].clone(),
                advantages[perm].clone(),
                fixed_log_probs[perm].clone(),
            )

            for i in range(optim_iter_num):
                ind = slice(
                    i * optim_batch_size,
                    min((i + 1) * optim_batch_size, states.shape[0]),
                )
                states_b, actions_b, advantages_b, returns_b, fixed_log_probs_b = (
                    states[ind],
                    actions[ind],
                    advantages[ind],
                    returns[ind],
                    fixed_log_probs[ind],
                )

                ppo_step(
                    policy_net,
                    value_net,
                    optimizer_policy,
                    optimizer_value,
                    1,
                    states_b,
                    actions_b,
                    returns_b,
                    advantages_b,
                    fixed_log_probs_b,
                    args.clip_epsilon,
                    args.l2_reg,
                )

    def main_loop():

        ppo_rewards = []
        for i_iter in range(args.max_iter_num):
            """generate multiple trajectories that reach the minimum batch_size"""
            batch, log = agent.collect_samples(args.min_batch_size, render=args.render)
            t0 = time.time()
            update_params(batch, i_iter)
            t1 = time.time()
            """evaluate with determinstic action (remove noise for exploration)"""
            _, log_eval = agent.collect_samples(args.eval_batch_size, mean_action=False)
            t2 = time.time()
            ppo_rewards.append(log_eval["avg_reward"])
            if i_iter % args.log_interval == 0:
                print(
                    "{}\tT_sample {:.4f}\tT_update {:.4f}\tT_eval {:.4f}\ttrain_R_min {:.2f}\ttrain_R_max {:.2f}\ttrain_R_avg {:.2f}\teval_R_avg {:.2f}".format(
                        i_iter,
                        log["sample_time"],
                        t1 - t0,
                        t2 - t1,
                        log["min_reward"],
                        log["max_reward"],
                        log["avg_reward"],
                        log_eval["avg_reward"],
                    )
                )

            if (
                args.save_model_interval > 0
                and (i_iter + 1) % args.save_model_interval == 0
            ):
                to_device(torch.device("cpu"), policy_net, value_net)
                pickle.dump(
                    (policy_net, value_net, running_state),
                    open(
                        os.path.join(
                            assets_dir(),
                            "learned_models/{}_ppo.p".format(args.env_name),
                        ),
                        "wb",
                    ),
                )
                to_device(device, policy_net, value_net)

            if max(ppo_rewards) == log_eval["avg_reward"]:
                torch.save(policy_net, "./model_best.pt")

            """clean up gpu memory"""
            torch.cuda.empty_cache()
        return ppo_rewards

    def eval_loop(num_episodes, agent_type, env_cls, env_config):

        # instantiate env class
        env_config.update({"seed": 10})
        env = env_cls(env_config)
        if agent_type == "PPO":
            model = torch.load("./model_best.pt")
            model.to("cpu")
            model.eval()
        elif agent_type == "CQI":
            model = MaxCQIAgent()
        elif agent_type == "Pressure":
            model = MaxPressureAgent()

        episode_rewards = []
        forward_pass_times = []
        for episode in range(num_episodes):
            episode_reward = 0
            done = False
            obs = env.reset()
            while not done:
                if agent_type == "PPO":
                    obs = torch.from_numpy(obs)
                    obs = torch.unsqueeze(obs, dim=0)
                    start = time.time()
                with torch.no_grad():
                    action = model.select_action(obs)
                    if agent_type == "PPO":
                        forward_pass_times.append(time.time() - start)
                        action = torch.squeeze(action)

                obs, reward, done, info = env.step(action)
                episode_reward += reward
            episode_rewards.append(episode_reward)
        if agent_type == "PPO":
            return episode_rewards, forward_pass_times
        return episode_rewards

    num_eval_episodes = 100
    ppo_train_rewards = main_loop()

    ppo_agent_rewards, forward_pass_times = eval_loop(
        num_eval_episodes, "PPO", env_cls, conf["env_config"]
    )

    max_cqi_agent_rewards = eval_loop(
        num_eval_episodes, "CQI", env_cls, conf["env_config"]
    )
    max_pressure_agent_rewards = eval_loop(
        num_eval_episodes, "Pressure", env_cls, conf["env_config"]
    )

    visualize_edgeric(
        ppo_train_rewards,
        ppo_agent_rewards,
        max_cqi_agent_rewards,
        max_pressure_agent_rewards,
    )
    plot_cdf(forward_pass_times)


if __name__ == "__main__":
    main()
