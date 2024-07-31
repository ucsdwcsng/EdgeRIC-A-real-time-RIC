import argparse
import hydra
import gym
import os
import sys
import pickle
import time
import debugpy
import logging
import torch
import numpy as np
import zmq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import time
from edgeric_messenger import *

torch.set_printoptions(precision=2)
np.set_printoptions(suppress=True)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from models.mlp_policy import Policy
from models.mlp_critic import Value
from models.mlp_policy_disc import DiscretePolicy
from core.ppo import ppo_step
from core.common import estimate_advantages
from core.agent_original import Agent

from stream_rl.registry import ENVS
from stream_rl.plots import (
    visualize_edgeric_training,
    visualize_edgeric_evaluation,
    plot_cdf,
    visualize_policy_cqi,
    visualize_policy_backlog_len,
)

# A logger for this file
log = logging.getLogger(__name__)


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
    default=0.9,
    metavar="G",
    help="discount factor (default: 0.99)",
)
parser.add_argument(
    "--tau", type=float, default=0.95, metavar="G", help="gae (default: 0.95)"
)
parser.add_argument(
    "--l2-reg",
    type=float,
    default=1e-2,
    metavar="G",
    help="l2 regularization regression (default: 1e-3)",
)
parser.add_argument(
    "--learning-rate",
    type=float,
    default=3e-3,
    metavar="G",
    help="learning rate (default: 3e-3)",
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
    help="number of threads for agent (default: 1)",
)
parser.add_argument(
    "--seed", type=int, default=1, metavar="N", help="random seed (default: 1)"
)
parser.add_argument(
    "--min-batch-size",
    type=int,
    default=2048, #2048,
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
)  # Depreciated : Use num_iters field in config file instead
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

@hydra.main(config_path="conf", config_name="edge_ric") #, version_base=None)
def main(conf):

    dtype = torch.float32
    torch.set_default_dtype(dtype)
    device = (
        torch.device("cuda", index=args.gpu_index)
        if torch.cuda.is_available()
        else torch.device("cpu")
        #else map_location=torch.device('cpu')
    )
    if torch.cuda.is_available():
        torch.cuda.set_device(args.gpu_index)

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
        hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
        output_dir = hydra_cfg["run"]["dir"]
         # Ensure the directory exists
        if not os.path.exists(output_dir):
            print(f"Creating directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        else:
            print(f"Directory already exists: {output_dir}")
        #output_dir = "/home/wcsng-24/Ushasi/Pytorch-RL-Custom_mobicom/simulator/Pytorch-RL-Custom_mobicom/simulator/outputs/Ushasi"
        ppo_rewards = []
        for i_iter in range(conf["num_iters"]):
            """generate multiple trajectories that reach the minimum batch_size"""
            batch, log_train = agent.collect_samples(
                args.min_batch_size, render=args.render
            )
            t0 = time.time()
            update_params(batch, i_iter)
            t1 = time.time()
            """evaluate with determinstic action (remove noise for exploration)"""
            _, log_eval = agent.collect_samples(args.eval_batch_size, mean_action=False)
            t2 = time.time()
            ppo_rewards.append(log_eval["avg_reward"]/5000) 
            if i_iter % args.log_interval == 0:
                log.info(
                    "{}\tT_sample {:.4f}\tT_update {:.4f}\tT_eval {:.4f}\ttrain_R_min {:.2f}\ttrain_R_max {:.2f}\ttrain_R_avg {:.2f}\teval_R_avg {:.2f}".format(
                        i_iter,
                        log_train["sample_time"],
                        t1 - t0,
                        t2 - t1,
                        log_train["min_reward"],
                        log_train["max_reward"],
                        log_train["avg_reward"],
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

            if max(ppo_rewards) == log_eval["avg_reward"]/5000:
                torch.save(policy_net, os.path.join(output_dir, "model_best.pt"))

            if i_iter == 1 or i_iter == 15:
                filename = f"model_{i_iter}.pt"
                model_path = os.path.join(output_dir, filename)
                torch.save(policy_net, model_path)


            """clean up gpu memory"""
            torch.cuda.empty_cache()
        return ppo_rewards

    def eval_loop(num_episodes, agent_type, env_cls, env_config):
        log.info(f"\n\n {agent_type}")
        #hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
        #output_dir = hydra_cfg["runtime"]["output_dir"]
        output_dir = "/home/wcsng-24/Ushasi/Pytorch-RL-Custom_mobicom/simulator/Pytorch-RL-Custom_mobicom/simulator/outputs/2023-02-01/17-19-06" #4ue: /2023-01-31/22-03-04" #RW :2023-02-01/17-19-06
        # instantiate env class
        env_config.update({"seed": 9})
        env_config.update({"cqi_trace": env_config["cqi_trace_eval"]})
        env = env_cls(env_config)
        if agent_type == "PPO":
            model = torch.load(os.path.join(output_dir, "model_best.pt"), map_location=torch.device('cpu'))
            #model.to("cpu")
            model.eval()
        elif agent_type == "CQI":
            model = MaxCQIAgent(env_config["augment_state_space"])
        elif agent_type == "Pressure":
            model = MaxPressureAgent(env_config["augment_state_space"])

        episode_rewards = []
        forward_pass_times = []
        for episode in range(num_episodes):
            log.info(f"Episode {episode}")
            episode_reward = 0
            done = False
            ue_data = get_metrics_multi()
            numues = len(ue_data)
            env.num_UEs = numues
            obs = env.reset()
            #for _ in range(1000000):
            while not done:
                curr_state = obs
                if agent_type == "PPO":
                    obs = torch.from_numpy(obs)
                    obs = torch.unsqueeze(obs, dim=0)
                    start = time.time()
                with torch.no_grad():
                    start = time.time()
                    action = model.select_action(obs)
                    socket_send_computetime.send_string(str(time.time() - start))
                    #start = time.time()
                    if agent_type == "PPO":
                        forward_pass_times.append(time.time() - start)
                        action = torch.squeeze(action)
                ue_data = get_metrics_multi()
                
                numues = len(ue_data)
                weight = np.zeros(numues * 2)
                # Extract CQIs and RNTIs and BLs from ue_data
                CQIs = [data['CQI'] for data in ue_data.values()]
                RNTIs = list(ue_data.keys())
                BLs = [data['Backlog'] for data in ue_data.values()]
                mbs = np.ones(numues)*300000 
                txb = [data['Backlog'] for data in ue_data.values()]   
                tx_bytes = np.sum(txb)   
                        
                obs, reward, done, info = env.step(action, RNTIs, CQIs, BLs, tx_bytes, MBs)

                for ue in range(numues):

                    percentage_RBG = action[ue] / sum(action)
                    
                    weight[ue*2+1] = percentage_RBG
                    weight[ue*2] = RNTIs[ue]

                send_scheduling_weight(weight, True) 
                

                log.info(
                    f"state: {curr_state} action: {action} next_state: {obs} reward: {reward}"
                )
                episode_reward += reward
            episode_reward = episode_reward/1000.0   
            episode_rewards.append(episode_reward)
        if agent_type == "PPO":
            return episode_rewards, forward_pass_times
        return episode_rewards

    num_eval_episodes = conf["num_eval_episodes"]
    num_seeds = conf["num_seeds"]
    ppo_train_rewards = []
    env_cls = ENVS[conf["env"]]
    env = env_cls(conf["env_config"])
    
    
    for seed in range(num_seeds):
        log.info(f"********* Training for seed {seed+1} *********")
        """environment"""
        env_cls = ENVS[conf["env"]]
        env = env_cls(conf["env_config"])
        state_dim = env.observation_space.shape[0]
        is_disc_action = len(env.action_space.shape) == 0
        running_state = None
        # running_state = ZFilter((state_dim,), clip=5)
        # running_reward = ZFilter((1,), demean=False, clip=10)

        """seeding"""
        # np.random.seed(args.seed)
        # torch.manual_seed(args.seed)
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
            policy_net, value_net, running_state = pickle.load(
                open(args.model_path, "rb")
            )
        policy_net.to(device)
        value_net.to(device)

        optimizer_policy = torch.optim.Adam(
            policy_net.parameters(), lr=args.learning_rate
        )
        optimizer_value = torch.optim.Adam(
            value_net.parameters(), lr=args.learning_rate
        )

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

        ppo_train_rewards.append(main_loop())
    
    if ppo_train_rewards:
        visualize_edgeric_training(
            ppo_train_rewards
        )
        #visualize_policy_cqi()
        #visualize_policy_backlog_len()
    

    
    
    '''
    
    log.info(f"********* Running Evaluation *********")

    
    ppo_agent_rewards, forward_pass_times = eval_loop(
        num_eval_episodes, "PPO", env_cls, conf["env_config"]
    )

    
    
    max_cqi_agent_rewards = eval_loop(
        num_eval_episodes, "CQI", env_cls, conf["env_config"]
    )

    
    max_pressure_agent_rewards = eval_loop(
        num_eval_episodes, "Pressure", env_cls, conf["env_config"]
    )
    
    
    log.info(f"PPO Agent mean reward : {np.mean(ppo_agent_rewards)}")

    

    log.info(f"MaxPressure Agent mean reward : {np.mean(max_pressure_agent_rewards)}")
    log.info(f"MaxCQI Agent mean reward : {np.mean(max_cqi_agent_rewards)}")

    
    visualize_edgeric_evaluation(
        ppo_agent_rewards,
        max_cqi_agent_rewards,
        max_pressure_agent_rewards,
    )
    # plot_cdf(forward_pass_times)
    
   ''' 
    

if __name__ == "__main__":
    main()
