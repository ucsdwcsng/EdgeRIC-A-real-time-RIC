import argparse
from collections import defaultdict
from datetime import datetime
import gym
import os
import sys
import pickle
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from utils import *
from models.mlp_policy import Policy
from models.mlp_critic import Value
from models.mlp_policy_disc import DiscretePolicy
from core.ppo import ppo_step
from core.common import estimate_advantages
from core.agent import Agent
from envs.downLinkEnv import downLinkEnv
from envs.downLinkEnvProto import downLinkEnvProto
from envs.downLinkEnvProtoRAN import downLinkEnvProtoRAN
from torch.utils.tensorboard import SummaryWriter
from plot import plot_thresh_policy

parser = argparse.ArgumentParser(description='PyTorch PPO example')
parser.add_argument('--env-name', default="down_link_proto_ran", metavar='G',
                    help='name of the environment to run')
parser.add_argument('--model-path', metavar='G',
                    help='path of pre-trained model')
parser.add_argument('--render', action='store_true', default=False,
                    help='render the environment')
parser.add_argument('--log-std', type=float, default=-0.0, metavar='G',
                    help='log std for the policy (default: -0.0)')
parser.add_argument('--gamma', type=float, default=0.99, metavar='G',
                    help='discount factor (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.95, metavar='G',
                    help='gae (default: 0.95)')
parser.add_argument('--l2-reg', type=float, default=1e-3, metavar='G',
                    help='l2 regularization regression (default: 1e-3)')
parser.add_argument('--learning-rate', type=float, default=3e-4, metavar='G',
                    help='learning rate (default: 3e-4)')
parser.add_argument('--clip-epsilon', type=float, default=0.2, metavar='N',
                    help='clipping epsilon for PPO')
parser.add_argument('--num-threads', type=int, default=1, metavar='N',
                    help='number of threads for agent (default: 1)')
parser.add_argument('--seed', type=int, default=1, metavar='N',
                    help='random seed (default: 1)')
parser.add_argument('--min-batch-size', type=int, default=900, metavar='N',
                    help='minimal batch size per PPO update (default: 2048)')
parser.add_argument('--eval-batch-size', type=int, default=300, metavar='N',
                    help='minimal batch size for evaluation (default: 2048)')
parser.add_argument('--max-iter-num', type=int, default=500, metavar='N',
                    help='maximal number of main iterations (default: 500)')
parser.add_argument('--log-interval', type=int, default=1, metavar='N',
                    help='interval between training status logs (default: 10)')
parser.add_argument('--save-model-interval', type=int, default=10, metavar='N',
                    help="interval between saving model (default: 0, means don't save)")
parser.add_argument('--gpu-index', type=int, default=0, metavar='N')
parser.add_argument('--run-tag', type=str, help='tag to label log dir for easy lookup on tensorboard')
args = parser.parse_args()

dtype = torch.float64
torch.set_default_dtype(dtype)
device = torch.device('cuda', index=args.gpu_index) if torch.cuda.is_available() else torch.device('cpu')
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
    advantages, returns = estimate_advantages(rewards, masks, values, args.gamma, args.tau, device)

    """perform mini-batch PPO update"""
    optim_iter_num = int(math.ceil(states.shape[0] / optim_batch_size))
    for _ in range(optim_epochs):
        perm = np.arange(states.shape[0])
        np.random.shuffle(perm)
        perm = LongTensor(perm).to(device)

        states, actions, returns, advantages, fixed_log_probs = \
            states[perm].clone(), actions[perm].clone(), returns[perm].clone(), advantages[perm].clone(), fixed_log_probs[perm].clone()

        for i in range(optim_iter_num):
            ind = slice(i * optim_batch_size, min((i + 1) * optim_batch_size, states.shape[0]))
            states_b, actions_b, advantages_b, returns_b, fixed_log_probs_b = \
                states[ind], actions[ind], advantages[ind], returns[ind], fixed_log_probs[ind]

            ppo_step(policy_net, value_net, optimizer_policy, optimizer_value, 1, states_b, actions_b, returns_b,
                     advantages_b, fixed_log_probs_b, args.clip_epsilon, args.l2_reg)


def main_loop():
    data_dump = defaultdict(list)
    for i_iter in range(args.max_iter_num):
        """generate multiple trajectories that reach the minimum batch_size"""
        batch, log = agent.collect_samples(args.min_batch_size, render=args.render)
        t0 = time.time()
        #Learning part#############
        update_params(batch, i_iter)
        ############################
        t1 = time.time()
        """evaluate with determinstic action (remove noise for exploration)"""
        _, log_eval = agent.collect_samples(args.eval_batch_size, mean_action=False)
        t2 = time.time()

        if i_iter % args.log_interval == 0:
            print('{}\tT_sample {:.4f}\tT_update {:.4f}\tT_eval {:.4f}\ttrain_R_min {:.2f}\ttrain_R_max {:.2f}\ttrain_R_avg {:.2f}\teval_R_avg {:.2f}\ttrain_stalls {:.2f}\teval_stalls {:.2f}\ttrain_MB_avg {:.2f}\teval_MB_avg {:.2f}'.format(
                i_iter, log['sample_time'], t1-t0, t2-t1, log['min_reward'], log['max_reward'], log['avg_reward'], log_eval['avg_reward'], log['avg_stalls'], log_eval['avg_stalls'], log['MB_avg'], log_eval['MB_avg']))
            data_dump['iter'].append(i_iter)
            data_dump['T_sample'].append(log['sample_time'])
            data_dump['T_update'].append(t1-t0)
            data_dump['T_eval'].append(t2-t1)
            data_dump['train_R_min'].append(log['min_reward'])
            data_dump['train_R_max'].append(log['max_reward'])
            data_dump['train_R_avg'].append(log['avg_reward'])
            data_dump['eval_R_avg'].append(log_eval['avg_reward'])
            data_dump['train_stalls'].append(log['avg_stalls'])
            data_dump['eval_stalls'].append(log_eval['avg_stalls'])
            data_dump['train_MB_avg'].append(log['MB_avg'])
            data_dump['eval_MB_avg'].append(log_eval['MB_avg'])
            writer.add_scalar(f'rewards/train_R_avg',log['avg_reward'],i_iter+1)
            writer.add_scalar(f'rewards/eval_R_avg',log_eval['avg_reward'],i_iter+1)
            writer.add_scalar(f'stalls/train',log['avg_stalls'],i_iter+1)
            writer.add_scalar(f'stalls/eval',log_eval['avg_stalls'],i_iter+1)
            writer.add_scalar(f'MB_avg/train',log['MB_avg'],i_iter+1)
            writer.add_scalar(f'MB_avg/eval',log_eval['MB_avg'],i_iter+1)

        if args.save_model_interval > 0 and (i_iter+1) % args.save_model_interval == 0:
            to_device(torch.device('cpu'), policy_net, value_net)
            os.makedirs( os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}'), exist_ok = True)
            pickle.dump((policy_net, value_net, running_state),
                        open(os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}','{}_lambda{}_ppo.p'.format(args.env_name,COST)), 'wb'))
            to_device(device, policy_net, value_net)
            df = pd.DataFrame(data=data_dump)
            df.to_csv(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}','{}_lambda{}_ppo.csv'.format(args.env_name,COST)))

        """clean up gpu memory"""
        torch.cuda.empty_cache()


"""environment"""
BATCHSIZE = 5 #Dummy
EPISODELIMIT = 300
numEpisodes = 2000 #Dummy
TRAIN = True
noiseVar = 0.0 #Dummy
SEED = 50
COSTS = [  0.5, 0.75, 1.5, 3, 5 ]
timestamp = datetime.now()
for COST in COSTS: 
    if args.env_name == "down_link_proto":
        env = downLinkEnvProto(numEpisodes=numEpisodes, seed=SEED, Training=TRAIN, r1=10, high_RB=40,low_RB = 20, maxBufferSize=500, batchSize=BATCHSIZE,
    episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = COST)
    elif args.env_name == "down_link":
        env = downLinkEnv(numEpisodes=numEpisodes, seed=SEED, Training=TRAIN, r1=3000, high_RB=12,low_RB = 6, maxBufferSize=75000, batchSize=BATCHSIZE,
    episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = COST) 
    elif args.env_name == "down_link_proto_ran":
        env = downLinkEnvProtoRAN(numEpisodes=numEpisodes, seed=SEED, Training=TRAIN, r1=2*517, high_RB=40,low_RB = 20, maxBufferSize=10000, batchSize=BATCHSIZE,
    episodeLimit=EPISODELIMIT,fixedSizeMDP=False,noiseVar=noiseVar, cost = COST) 
    else: 
        env = gym.make(args.env_name) 
    state_dim = env.observation_space.shape[0]
    is_disc_action = len(env.action_space.shape) == 0
    # running_state = ZFilter((state_dim,), clip=5)
    running_state = None
    # running_reward = ZFilter((1,), demean=False, clip=10)

    """seeding"""
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    # env.seed(SEED)

    """define actor and critic"""
    if args.model_path is None:
        if is_disc_action:
            policy_net = DiscretePolicy(state_dim, env.action_space.n)
        else:
            policy_net = Policy(state_dim, env.action_space.shape[0], log_std=args.log_std)
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
    agent = Agent(env, policy_net, device, running_state=running_state, num_threads=args.num_threads)

    """Run"""
    writer = SummaryWriter(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}',f'lambda_{COST}'))
    writer.add_text('Cost',str(COST))
    writer.add_text('high_RB',str(env.high_RB))
    writer.add_text('low_RB',str(env.low_RB))
    main_loop()
plot_thresh_policy(args.env_name,COSTS,args.run_tag,env.observation_space)
