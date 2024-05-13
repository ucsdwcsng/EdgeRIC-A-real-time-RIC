#export PYTHONPATH=$PYTHONPATH:/home/wcsng-24/.local/lib/python3.8/site-packages
import argparse
import zmq
from collections import defaultdict
from datetime import datetime
#import sys
#sys.path.append('/home/wcsng-24/.local/lib/python3.8/site-packages/gym')
import gym
import os
import sys
import pickle
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import datetime
import math
from utils import *
from models.mlp_policy import Policy
from models.mlp_critic import Value
from models.mlp_policy_disc import DiscretePolicy
from core.ppo import ppo_step
from core.common import estimate_advantages
from core.agent import Agent
from envs.downLinkEnv import downLinkEnv
from envs.twoArmRAN import twoArmRAN
from envs.multiArmRAN import multiArmRAN
from envs.downLinkEnvProto import downLinkEnvProto
from envs.downLinkEnvProtoRAN import downLinkEnvProtoRAN
from envs.multiArmWrapper import multiArmWrapper
from torch.utils.tensorboard import SummaryWriter
from plot import plot_thresh_policy

parser = argparse.ArgumentParser(description='PyTorch PPO example')
parser.add_argument('--env-name', default="two_arm_ran", metavar='G',
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
#parser.add_argument('--learning-rate', type=float, default=3e-4, metavar='G',
parser.add_argument('--learning-rate', type=float, default=1e-5, metavar='G',
                    #help='learning rate (default: 3e-4)')
                    help='learning rate (default: 1e-5)')
parser.add_argument('--clip-epsilon', type=float, default=0.2, metavar='N',
                    help='clipping epsilon for PPO')
parser.add_argument('--num-threads', type=int, default=1, metavar='N',
                    help='number of threads for agent (default: 1)')
parser.add_argument('--num-arms', type=int, default=2, metavar='N',
                    help='number of UEs (default: 2)')
parser.add_argument('--schedule-arms', type=int, default=1, metavar='N',
                    help='number of UEs to give high action to per TTI (default: 1)')
parser.add_argument('--seed', type=int, default=1, metavar='N',
                    help='random seed (default: 1)')
#parser.add_argument('--min-batch-size', type=int, default=900, metavar='N',
parser.add_argument('--min-batch-size', type=int, default=2000, metavar='N',
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

#print(args.run_tag)
dtype = torch.float64
torch.set_default_dtype(dtype)
device = torch.device('cuda', index=args.gpu_index) if torch.cuda.is_available() else torch.device('cpu')
if torch.cuda.is_available():
    torch.cuda.set_device(args.gpu_index)

context = zmq.Context()
print("zmq context created")
socket_send_computetime = context.socket(zmq.PUB)
socket_send_computetime.bind("ipc:///tmp/socket_riccompute")



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


def eval_loop_weight(eval_episodes):
    test_data_dump = defaultdict(list)
    print("Starting Test Episodes..............")
    
    #Weight-based TODO extend this to any num of UEs and not just 2!!
    print("\nWeight-based:")
    
    
    for i_episode in range(eval_episodes):
        possible_actions = [0,1]
        ###state = env.reset()
        ##if i_episode%10 == 0:
        ##    print(state)
        reward_episode = 0
        stalls_episode = 0
        cnt = 0
        flag = True
        prev_weight_x = 0.51
        prev_weight_y = 0.49

        prev_weights = np.zeros(env.numArms)
        
        avg_CQI_x = 0 
        avg_CQI_y = 0 
        avg_CQIs = np.zeros(env.numArms) 
        
        print("\n\n\n",i_episode, "\n\n\n")
        
        for _ in range(10000):
            cnt = cnt + 1
            if (cnt >=1000): flag = True
           
            
            #monitoring_cqis(flag)
            
            #rnti_weights = fixed_weights(flag)

            #rnti_weights, prev_weight_x, prev_weight_y = algo1_cqi(prev_weight_x, prev_weight_y, flag)
            #rnti_weights, prev_weight_x, prev_weight_y = algo1(prev_weight_x, prev_weight_y, flag)
           
            # algo1 Max CQI
            #rnti_weights, prev_weight_x, prev_weight_y = algo1_maxCQI(prev_weight_x, prev_weight_y, flag)
            #rnti_weights, prev_weights = algo1_maxCQI_multi(prev_weights, flag)
            
            # algo2 propFair
            #rnti_weights, prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y = algo2_propFair(prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y, flag)
            #rnti_weights, prev_weights, avg_CQIs = algo2_propFair_multi(prev_weights, avg_CQIs, flag)

            # algo3 Max-Weight
            #rnti_weights, prev_weight_x, prev_weight_y = algo3_maxWeight(prev_weight_x, prev_weight_y, flag)
            start = time.time()
            rnti_weights, prev_weights = algo3_maxWeight_multi(prev_weights, flag)
            socket_send_computetime.send_string(str(time.time() - start))
            env.send_weight(rnti_weights,flag)
            
            
            
            
            if(flag == True):
                #print("Weights sent to RAN: ", rnti_weights, "\n")
                cnt = 0
                flag = False

         


def algo1_maxCQI_multi(prev_weights, flag):
    RNTIs, CQIs, BLs = env.get_metrics_multi() # to make get_metrics() to return backlogs as well

    #if (flag == True): print("Metrics received from RAN: ", RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y)
    
    weights = np.zeros(env.numArms*2)
    
    
    high = 1-(env.numArms*0.1)
    low = 0.1

    if (min(CQIs) > 0): 
        maxIndex = np.argmax(CQIs)
        new_weights = np.zeros(env.numArms)
               
        high = 1-((env.numArms-1)*0.1)
        low = 0.1
        for i in range(env.numArms):
            if i == maxIndex:
                new_weights[i] = high
                weights[i*2+0] = RNTIs[i]
                weights[i*2+1] = new_weights[i]
            else:
                new_weights[i] = low
                weights[i*2+0] = RNTIs[i]
                weights[i*2+1] = new_weights[i]

        
        
        
        #weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
        
        prev_weights = new_weights
        
    else:  
        
        #weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
        for i in range(env.numArms):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = prev_weights[i]
            
    
    return weights, prev_weights

def algo2_propFair_multi(prev_weights, avg_CQIs, flag):
    RNTIs, CQIs, BLs = env.get_metrics_multi() # to make get_metrics() to return backlogs as well
    weights = np.zeros(env.numArms*2)
   
    
    if (min(CQIs)>0): 
        gamma = 0.1 
        if(avg_CQIs[0] == 0): avg_CQIs[0]=CQIs[0]
        if(avg_CQIs[1] == 0): avg_CQIs[1]=CQIs[1]
        #if(avg_CQIs[2] == 0): avg_CQIs[2]=CQIs[2]
        #if(avg_CQIs[3] == 0): avg_CQIs[3]=CQIs[3]
        
        
        #avg_CQI_x = avg_CQI_x*(1-gamma) + CQI_x*(gamma)
        #avg_CQI_y = avg_CQI_y*(1-gamma) + CQI_y*(gamma)
        avg_CQIs = avg_CQIs*(1-gamma) + CQIs*(gamma)
        
        #Unnormalized weights
        temp_weights = CQIs/avg_CQIs 
        #print (temp_weights,CQI_x, avg_CQI_x, CQI_y, avg_CQI_y )
        
        new_weights = np.round(temp_weights/(np.sum(temp_weights)), 2)
        #new_weight_y = round(1-new_weight_x, 2)
        
        
        prev_weights = new_weights

        for i in range(env.numArms):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = prev_weights[i]
        
    else:
        for i in range(env.numArms):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = prev_weights[i]

    
    return weights, prev_weights, avg_CQIs



def algo3_maxWeight_multi(prev_weights, flag):
    RNTIs, CQIs, BLs = env.get_metrics_multi() # to make get_metrics() to return backlogs as well
    #print(RNTIs)
    weights = np.zeros(env.numArms*2)
    #print(weights)
    #RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y = env.get_metrics() # to make get_metrics() to return backlogs as well

    #if (flag == True): print("Metrics received from RAN: ", RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y)

    #print(RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y)


    if (min(CQIs) > 0): 
        sum_CQI = np.sum(CQIs)
        sum_BL = np.sum(BLs) 
        if (sum_BL != 0):
            new_weights = CQIs/sum_CQI * BLs/sum_BL
            
        else:
            new_weights = CQIs/sum_CQI
            
        
        new_weights_norm = np.round((new_weights/np.sum(new_weights)*100)/100)
        prev_weights = new_weights
        #weights[1] = 0.65
        #weights[3] = 0.35

        for i in range(env.numArms):
            #print(RNTIs[i])
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = prev_weights[i]
            #print(weights)
            #weights[i*2+1] = 0.65
        

        
        
    else:  
        weights[1] = 0.65
        weights[3] = 0.35
        for i in range(env.numArms):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = prev_weights[i]
            #weights[i*2+1] = 0.5
    
    return weights, prev_weights 


    

def eval_loop(eval_episodes):
    test_data_dump = defaultdict(list)
    print("Starting Test Episodes..............")
    
  

    #PPO Policy
    print("\n\nPPO")
    PPOrewards = []
    PPOstalls = []
    path_model = "/home/afc/git/Pytorch-RL-Custom_mobicom/assets/learned_models/two_arm_ran_" + args.run_tag + "/two_arm_ran_ppo.p"
    #policy_net, value_net, running_state = pickle.load(open("/home/afc/git/Pytorch-RL-Custom_mobicom/assets/learned_models/two_arm_ran_Woo_Hyun_08172022_10m_11/two_arm_ran_ppo.p", "rb")); 
    policy_net, value_net, running_state = pickle.load(open(path_model, "rb")); 
    # env = twoArmRAN( seed=SEED, numEpisodes=numEpisodes,  Training=TRAIN, r1=789,  high_RB=789, low_RB=789, maxBufferSize=50000000, batchSize=5, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, noiseVar=0, cost=0, zmq_params=None)
    for i_episode in range(eval_episodes):
        state = env.reset()
        if i_episode%10 == 0:
            print(state)
        reward_episode = 0
        stalls_episode = 0

        for _ in range(10000):

            #count stalls:
            MBs = state[0::2]
            for media_buffer in MBs:
                if media_buffer<=0:
                    stalls_episode += 1

            
            state_var = tensor(state).unsqueeze(0).to(dtype).to(device)
            ##print(agent.policy.select_action(state_var), policy_net(state_var))
            # a=input("hg")
            #action_v = agent.policy(state_var)[0].detach().cpu().numpy()
            action_v = agent.policy.select_action(state_var)[0].detach().cpu().numpy()
            
            
            #action = np.argmax(action_v)
            action = int(action_v[0]) 
            #action_v = policy_net(state_var)[0].detach().cpu().numpy()
            
            # action = int(action) if is_disc_action else action.astype(np.float64)
            
            # a=input("blah")
            #print("eval_loop", action_v, action)
            #next_state, reward, done, _ = env.step(action)
            next_state, reward, done, _ = env.step(action)
            reward_episode += reward
            if done:
                break 
            state = next_state

        print('Episode {}\t reward: {:.2f}'.format(i_episode, reward_episode))
        PPOrewards.append(reward_episode)
        PPOstalls.append(stalls_episode)
        
        #log all test metrics
        writer.add_scalars(f'Testing/reward',{'PP0':PPOrewards[i_episode]},i_episode+1)
        writer.add_scalars(f'Testing/stalls',{'PP0':PPOstalls[i_episode]},i_episode+1)
        test_data_dump['i_episode'].append(i_episode)
        test_data_dump['PPOreward'].append(PPOrewards[i_episode])
        test_data_dump['PPOstalls'].append(PPOstalls[i_episode])
       
    df = pd.DataFrame(data=test_data_dump)
    df.to_csv(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}','{}_ppo_test.csv'.format(args.env_name)))
    
    print(f"GB -> mean={np.mean(GBrewards)} std={np.std(GBrewards)} total_stalls={np.sum(GBstalls)}")
    print(f"RR -> mean={np.mean(RRrewards)} std={np.std(RRrewards)} total_stallsi={np.sum(RRstalls)}")
    print(f"PPO -> mean={np.mean(PPOrewards)} std={np.std(PPOrewards)} total_stallsi={np.sum(PPOstalls)}")
    # test_summary = {'GB':{'mean':np.mean(GBrewards),'std':np.std(GBrewards)},
    #                 'RR':{'mean':np.mean(RRrewards),'std':np.std(RRrewards)},
    #                 'PPO':{'mean':np.mean(PPOrewards),'std':np.std(PPOrewards)}, 
    #          }

    # writer.add_custom_scalars(test_summary)
    


def main_loop():
    data_dump = defaultdict(list)
    for i_iter in range(args.max_iter_num):
        """generate multiple trajectories that reach the minimum batch_size"""
        #print("i_iter: ", i_iter)
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
            #print('{}\tT_sample {:.4f}\tT_update {:.4f}\tT_eval {:.4f}\ttrain_R_min {:.2f}\ttrain_R_max {:.2f}\ttrain_R_avg {:.2f}\teval_R_avg {:.2f}\ttrain_stalls {:.2f}\teval_stalls {:.2f}\ttrain_MB_avg {:.2f}\teval_MB_avg {:.2f}'.format(
            #    i_iter, log['sampleavg_tx_bytes_time'], t1-t0, t2-t1, log['min_reward'], log['max_reward'], log['avg_reward'], log_eval['avg_reward'], log['avg_stalls'], log_eval['avg_stalls'], log['MB_avg'], log_eval['MB_avg']))
            print('{}\tT_sample {:.4f}\tT_update {:.4f}\tT_eval {:.4f}\ttrain_R_min {:.2f}\ttrain_R_max {:.2f}\ttrain_R_avg {:.2f}\teval_R_avg {:.2f}\ttrain_stalls {:.2f}\teval_stalls {:.2f}\ttrain_BB_avg {:.2f}\teval_BB_avg {:.2f}'.format(
                i_iter, log['sample_time'], t1-t0, t2-t1, log['min_reward'], log['max_reward'], log['avg_reward'], log_eval['avg_reward'], log['avg_stalls'], log_eval['avg_stalls'], log['BB_avg'], log_eval['BB_avg']))
            
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
            #data_dump['train_MB_avg'].append(log['MB_avg'])
            data_dump['train_BB_avg'].append(log['BB_avg'])
            #data_dump['eval_MB_avg'].append(log_eval['MB_avg'])
            data_dump['eval_BB_avg'].append(log_eval['BB_avg'])
            writer.add_scalar(f'rewards/train_R_avg',log['avg_reward'],i_iter+1)
            writer.add_scalar(f'rewards/eval_R_avg',log_eval['avg_reward'],i_iter+1)
            writer.add_scalar(f'stalls/train',log['avg_stalls'],i_iter+1)
            writer.add_scalar(f'stalls/eval',log_eval['avg_stalls'],i_iter+1)
            #writer.add_scalar(f'MB_avg/train',log['MB_avg'],i_iter+1)
            writer.add_scalar(f'BB_avg/train',log['BB_avg'],i_iter+1)
            #writer.add_scalar(f'MB_avg/eval',log_eval['MB_avg'],i_iter+1)
            writer.add_scalar(f'BB_avg/eval',log_eval['BB_avg'],i_iter+1)

        if args.save_model_interval > 0 and (i_iter+1) % args.save_model_interval == 0:
            to_device(torch.device('cpu'), policy_net, value_net)
            os.makedirs( os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}'), exist_ok = True)
            pickle.dump((policy_net, value_net, running_state),
                        open(os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}','{}_ppo.p'.format(args.env_name)), 'wb'))
            #policy_net, value_net, running_state = pickle.load("/home/afc/07282022_edgeRIC_2ue_emul_Mobicom/Pytorch-RL-Custom/assets/learned_models/two_arm_ran_Woo_Hyun_4/two_arm_.p"); 
            #
            to_device(device, policy_net, value_net)
            
            df = pd.DataFrame(data=data_dump)
            df.to_csv(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}','{}_ppo.csv'.format(args.env_name)))

        """clean up gpu memory"""
        torch.cuda.empty_cache()

"""environment"""
BATCHSIZE = 5 #Dummy
EPISODELIMIT = 1000
numEpisodes = 2000 #Dummy
TRAIN = True
noiseVar = 0.0 #Dummy
SEED = 50
#timestamp = datetime.datetime.now()

# env = multiArmWrapper(numEpisodes=numEpisodes, seed=SEED, Training=TRAIN, r1=10, high_RB=40,low_RB = 20, maxBufferSize=500, batchSize=BATCHSIZE, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, 
#     noiseVar=noiseVar,singleArmEnvType=args.env_name, numArms=args.num_arms, scheduleArms=args.schedule_arms)
#env = twoArmRAN( seed=SEED, numEpisodes=numEpisodes,  Training=TRAIN, r1=789,  high_RB=789, low_RB=789, maxBufferSize=10000000, batchSize=5, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, noiseVar=0, cost=0, zmq_params=None)
env = multiArmRAN( seed=SEED, numEpisodes=numEpisodes,  Training=TRAIN, r1=789,  high_RB=789, low_RB=789, maxBufferSize=1000000, batchSize=5, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, noiseVar=0, cost=0, zmq_params=None, numArms=args.num_arms)
#env = multiArmRAN( seed=SEED, numEpisodes=numEpisodes,  Training=TRAIN, r1=789,  high_RB=789, low_RB=789, maxBufferSize=10000000, batchSize=5, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, noiseVar=0, cost=0, zmq_params=None, numArms=4)
state_dim = env.observation_space.shape[0]
##print("**************",env.action_space.n)
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
        print("Discrete Policy")
    else:
        policy_net = Policy(state_dim, env.action_space.shape[0], log_std=args.log_std)
        
    value_net = Value(state_dim)
else:
    policy_net, value_net, running_state = pickle.load(open(args.model_path, "rb"))
    print("Pre-trained model is used. ")
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
writer = SummaryWriter(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}'))
writer.add_text('high_RB',str(env.high_RB))
writer.add_text('low_RB',str(env.low_RB))
writer.add_text('num_arms',str(env.numArms))
writer.add_text('hi_arms',str(env.scheduleArms))
#main_loop()   ### for RL
#eval_loop(100)
eval_loop_weight(100)  ## testing for algos
