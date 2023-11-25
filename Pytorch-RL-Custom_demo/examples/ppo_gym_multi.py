import argparse
import os
import pickle
import sys
from collections import defaultdict
from datetime import datetime

import gym
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import time

from core.agent import Agent
from core.common import estimate_advantages
from core.ppo import ppo_step
from models.mlp_critic import Value
from models.mlp_policy import Policy
from models.mlp_policy_disc import DiscretePolicy
from torch.utils.tensorboard import SummaryWriter
from utils import *

from envs.multiArmRAN import multiArmRAN

import torch

import redis

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
print("max_iter_num", args.max_iter_num)

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


def eval_loop_weight(eval_episodes, idx_algo):
    test_data_dump = defaultdict(list)
    print("Starting Test Episodes..............")
    
    #Weight-based TODO extend this to any num of UEs and not just 2!!
    print("\nWeight-based:")

    f_params = open("params_edgeric.txt")
    line_rl_model = 2
    line_rl_model_1 = 3
    line_rl_model_2 = 4
    lines = f_params.readlines()
    rl_model_str = lines[line_rl_model].split()[0]
    
    print(rl_model_str)
    model = torch.load(rl_model_str, map_location=torch.device('cpu'))
    
    f_params.close()
    
    key_index = 0
    
    RRstalls = []
    for i_episode in range(eval_episodes):

        
        
        stalls_episode = 0
        cnt = 0
        flag = True
        prev_weight_x = 0.51
        prev_weight_y = 0.49

        prev_weights = np.zeros(env.numArms)
        
        avg_CQI_x = 0 ;  
        avg_CQI_y = 0 ; 
        
        MBs = zeros(args.num_arms)-1
        print("\n\n\ni_episode",i_episode, "\n\n\n")


        filename_stalls_timeseries = "stalls_" + str(idx_algo) +"_" + str(i_episode)+ ".txt"
        f_stalls_timeseries = open(filename_stalls_timeseries, "w")

        cnt_demo = 0

        key_algo = "algo"
        value_algo = "Half resource for each UE" # default algorithm

        
        for _ in range(1000000):
            cnt = cnt + 1
            if (cnt >=1000): 
                flag = True
                cnt = 0
            else :
                flag = False
            
            cnt_demo = cnt_demo + 1


            #monitoring_cqis(flag)
            if(idx_algo == -1):
                monitoring_cqis(flag)    
 
            if(idx_algo == 0):
                flag = False # to be deleted
                rnti_weights = fixed_weights(flag)
                env.send_weight(rnti_weights,flag)
                value_algo = "Fixed Weights"

            # algo1 Max CQI       
            if(idx_algo == 1):
                rnti_weights, prev_weight_x, prev_weight_y = algo1_maxCQI(prev_weight_x, prev_weight_y, flag, key_index)
                env.send_weight(rnti_weights,flag)
                value_algo = "MaxCQI"
                
            
            # algo2 propFair
            if(idx_algo == 2):
                rnti_weights, prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y = algo2_propFair(prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y, flag)
                env.send_weight(rnti_weights,flag)
                value_algo = "Proportional Fairness"
            
            # algo3 Max-Weight
            if(idx_algo == 3):
                rnti_weights, prev_weight_x, prev_weight_y, MBs = algo3_maxWeight(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries) 
                env.send_weight(rnti_weights,flag)
                value_algo = "MaxWeight"
                # 4. RIC transmits weights to RAN

            if(idx_algo == 4):
                rnti_weights, prev_weight_x, prev_weight_y, MBs = algo4_greedybuffer(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries)
                env.send_weight(rnti_weights,flag)
                value_algo = "Greedy Buffer"
            
            # algo5 Round Robin
            if(idx_algo == 5):
                rnti_weights, prev_weight_x, prev_weight_y, MBs = algo5_roundrobin(prev_weight_x, prev_weight_y, flag, cnt, f_stalls_timeseries)
                env.send_weight(rnti_weights,flag)
                value_algo = "Round Robin"
            
            # algo6 norm_CQI/norm_MB
            if(idx_algo == 6):
                rnti_weights, prev_weight_x, prev_weight_y, MBs = algo6_normCQIovernormMB(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries)
                env.send_weight(rnti_weights,flag)
                value_algo = "Normalized CQI over Normalized Media Buffer"


            # algo7 PPO
            if(idx_algo == 7):
                rnti_weights, prev_weight_x, prev_weight_y = algo7_ppo(prev_weight_x, prev_weight_y, flag, model, key_index)
                env.send_weight(rnti_weights,flag)
                value_algo =  "PPO"

            # Switching algorithms for a demo
            if(idx_algo == 9):                
                # Period to switch an algorithm
                period_per_algo = 5000
                
                
                if (cnt_demo > (0)*period_per_algo  and cnt_demo <= (0+1)*period_per_algo ) :
                    if (cnt_demo ==1 ): 
                        print('\nAlgorithm: MaxCQI\n')                        
                                           
                    
                    rnti_weights, prev_weight_x, prev_weight_y = algo1_maxCQI(prev_weight_x, prev_weight_y, flag, key_index)
                    value_algo = "MaxCQI"
                
                if (cnt_demo > (1)*period_per_algo and cnt_demo <= (1+1)*period_per_algo ) :
                    if (cnt_demo ==(1)*period_per_algo +1 ): 
                        print('\nAlgorithm: MaxWeight\n')
                        
                                                
                    rnti_weights, prev_weight_x, prev_weight_y, MBs = algo3_maxWeight(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries)
                    value_algo = "MaxWeight"
                
                if (cnt_demo > (2)* period_per_algo and cnt_demo <= (2+1)*period_per_algo ) :
                    if (cnt_demo == (2)*period_per_algo +1): 
                        print('\nAlgorithm: Half for each UE\n')
                        
                    rnti_weights= fixed_weights(flag)
                    value_algo = "Half resource for each UE"

                if (cnt_demo > (3)* period_per_algo and cnt_demo <= (3+1)*period_per_algo ) :
                    if (cnt_demo == (3)*period_per_algo +1): 
                        print('\nAlgorithm: PPO with initial model\n')

                        t0 = time.time()
                        
                        if redis_db_1 is not None: 
                            data_new = redis_db_1.get('rl_model_1')
                            if data_new is not None:
                                newFileNmae = "../rl_model/new_model_1.pt"; 
                                newFile = open(newFileNmae, "wb")
                                newFile.write(data_new)
                            else:
                                newFileNmae = rl_model_str
                        else:
                            newFileNmae = rl_model_str

                        model = torch.load(newFileNmae, map_location=torch.device('cpu'))
                        model.to(device)
                        model.eval()

                        t1 = time.time()
                        print("dt: " + str(t1-t0) )   
                           
                    rnti_weights, prev_weight_x, prev_weight_y = algo7_ppo(prev_weight_x, prev_weight_y, flag, model, key_index)
                    value_algo = "PPO with initial model"
                
                if (cnt_demo > (4)* period_per_algo and cnt_demo <= (4+1)*period_per_algo ) :
                    if (cnt_demo == (4)*period_per_algo +1): 
                        print('\nAlgorithm: PPO with half trained model\n')
                        

                        t0 = time.time()

                        if redis_db_1 is not None: 
                            data_new_1 = redis_db_1.get('rl_model_15')
                            if data_new_1 is not None:
                                newFileNmae_1 = "../rl_model/new_model_15.pt"; 
                                newFile_1 = open(newFileNmae_1, "wb")
                                newFile_1.write(data_new_1)
                            else:
                                newFileNmae_1 = rl_model_str
                        else:
                             newFileNmae_1 = rl_model_str
                        model_1 = torch.load(newFileNmae_1, map_location=torch.device('cpu'))
                        model_1.to(device)
                        model_1.eval()

                        t1 = time.time()
                        print("dt: " + str(t1-t0) )   
                        
                    rnti_weights, prev_weight_x, prev_weight_y = algo7_ppo(prev_weight_x, prev_weight_y, flag, model_1, key_index)
                    value_algo =  "PPO with half trained model"
                
                if (cnt_demo > (5)* period_per_algo and cnt_demo <= (5+1)*period_per_algo ) :
                    if (cnt_demo == (5)*period_per_algo +1): 
                        print('\nAlgorithm: PPO with fully trained model \n')
                        
                        t0 = time.time()

                        if redis_db_1 is not None: 
                            data_new_2 = redis_db_1.get('rl_model_best')
                            if data_new_2 is not None:
                                newFileNmae_2 = "../rl_model/new_model_best.pt"; 
                                newFile_2 = open(newFileNmae_2, "wb")
                                newFile_2.write(data_new_2)
                            else:
                                newFileNmae_2 = rl_model_str
                        else:
                            newFileNmae_2 = rl_model_str

                        model_2 = torch.load(newFileNmae_2, map_location=torch.device('cpu'))
                        model_2.to(device)
                        model_2.eval()

                        t1 = time.time()
                        print("dt: " + str(t1-t0) )                         
                        
                    rnti_weights, prev_weight_x, prev_weight_y = algo7_ppo(prev_weight_x, prev_weight_y, flag, model_2, key_index)
                    value_algo = "PPO with fully trained model"
                


                if (cnt_demo > (5+1)* period_per_algo):
                    cnt_demo = 0
                    

                env.send_weight(rnti_weights,flag)
            
  
            if(flag == True):
                cnt = 0
                flag = False
        
            
            for media_buffer in MBs:
                if media_buffer==0:
                    stalls_episode += 1
                
            

            redis_db.set(key_algo, value_algo)   
            
def is_redis_available(r):
    try: 
        r.ping()
        print("Successfully connected to redis")
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        print("Redis connection error!")
        return False
    return True

        
    
def monitoring_cqis(flag):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state()
    if (flag == True): print("Metrics received from RAN: ", RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y)


def fixed_weights(flag):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well
    
    if (flag == True): print("Metrics received from RAN: ", RNTI_x, CQI_x, BL_x, RNTI_y, CQI_y, BL_y)

 
    w1 = 0.5
    w2 = 0.5
    weights = [RNTI_x, w1, RNTI_y, w2]
    
    return weights

                
def algo1_maxCQI(prev_weight_x, prev_weight_y, flag, key_index):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well

	
    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)

    if (CQI_x > 0 and CQI_y > 0): 

        
        t0 = time.time()

        high = 0.9
        medium = 0.5
        low = 0.1
        if (CQI_x > CQI_y):
            new_weight_x = high
            new_weight_y = low

        
        elif(CQI_x < CQI_y):
            new_weight_x = low
            new_weight_y = high
            
        
        else:
            new_weight_x = medium
            new_weight_y = medium

        weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
        
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
    
    return weights, prev_weight_x, prev_weight_y




def algo2_propFair(prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y, flag):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well

    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)
    
    
    if (CQI_x > 0 and CQI_y > 0): 
        gamma = 0.01 
        if(avg_CQI_x == 0): avg_CQI_x = CQI_x
        if(avg_CQI_y == 0): avg_CQI_y = CQI_y
        
        avg_CQI_x = avg_CQI_x*(1-gamma) + CQI_x*(gamma)
        avg_CQI_y = avg_CQI_y*(1-gamma) + CQI_y*(gamma)
        
        
        temp_weights = [ CQI_x/avg_CQI_x, CQI_y/avg_CQI_y] 
        
        
        new_weight_x = round(temp_weights[0]/sum(temp_weights), 2)
        new_weight_y = round(1-new_weight_x, 2)
        
        weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
        
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
    
    return weights, prev_weight_x, prev_weight_y, avg_CQI_x, avg_CQI_y


 
def algo3_maxWeight(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well
    
    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)
    
    MBs = [MB_x , MB_y]
    


    if (CQI_x > 0 and CQI_y > 0): 
        sum_CQI = CQI_x + CQI_y
        sum_BL = BL_x + BL_y 
        if (sum_BL != 0):
            new_weight_x = CQI_x /sum_CQI * BL_x / sum_BL
            new_weight_y = CQI_y /sum_CQI * BL_y / sum_BL
        else:
            new_weight_x = CQI_x /sum_CQI
            new_weight_y = CQI_y /sum_CQI
        
        new_weight_x_norm = round(new_weight_x/(new_weight_x+new_weight_y)*100)/100
        new_weight_y_norm = round(new_weight_y/(new_weight_x+new_weight_y)*100)/100

        weights = [RNTI_x, new_weight_x_norm, RNTI_y, new_weight_y_norm]
        
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
 
    return weights, prev_weight_x, prev_weight_y, MBs


def algo4_greedybuffer(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well
    
    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)

    MBs = [MB_x , MB_y]
    
    if (CQI_x > 0 and CQI_y > 0): 
        high_weight = 0.9
        middle_weight = 0.5 
        low_weight = 1 - high_weight

        if MB_x < MB_y : 
            new_weight_x = high_weight
            new_weight_y = low_weight
        elif MB_x == MB_y :
            new_weight_x = middle_weight
            new_weight_y = middle_weight
        else:
            new_weight_x = low_weight
            new_weight_y = high_weight

        weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
            
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]

    return weights, prev_weight_x, prev_weight_y, MBs

def algo5_roundrobin(prev_weight_x, prev_weight_y, flag, cnt, f_stalls_timeseries):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well
    
    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)

    MBs = [MB_x , MB_y]
    
    if (CQI_x > 0 and CQI_y > 0): 
        high_weight = 0.9
        middle_weight = 0.5 
        low_weight = 1 - high_weight

        if cnt%args.num_arms == 0: 
            new_weight_x = high_weight
            new_weight_y = low_weight
        else:
            new_weight_x = low_weight
            new_weight_y = high_weight


        weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
            
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]

    return weights, prev_weight_x, prev_weight_y, MBs


def algo6_normCQIovernormMB(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well

    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)

    MBs = [MB_x , MB_y]
    
    max_CQI = 15
    max_BL = 1000000

    high_weight = 0.9
    middle_weight = 0.5 
    low_weight = 1 - high_weight


    if (CQI_x > 0 and CQI_y > 0): 
        sum_CQI = CQI_x + CQI_y
        #sum_BL = BL_x + BL_y 
        new_weight_x_norm = middle_weight
        new_weight_y_norm = middle_weight
        
        if (BL_x ==0 and BL_y > 0):
            new_weight_x = high_weight
            new_weight_y = low_weight
        
        elif BL_x > 0 and BL_y == 0: 
            new_weight_x = low_weight
            new_weight_y = high_weight

        elif BL_x == 0 and BL_y == 0: 
            new_weight_x = middle_weight
            new_weight_y = middle_weight
        
        else:
            
            new_weight_x = (CQI_x / max_CQI) / (BL_x/max_BL)
            new_weight_y = (CQI_y / max_CQI) / (BL_y/max_BL)
            
            if (new_weight_x > new_weight_y):
                new_weight_x_norm = high_weight
                new_weight_y_norm = low_weight
            elif (new_weight_x < new_weight_y):
                new_weight_x_norm = low_weight
                new_weight_y_norm = high_weight
            else:
                new_weight_x_norm = middle_weight
                new_weight_y_norm = middle_weight
      
        weights = [RNTI_x, new_weight_x_norm, RNTI_y, new_weight_y_norm]
        
        prev_weight_x = new_weight_x_norm
        prev_weight_y = new_weight_y_norm
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
    
    return weights, prev_weight_x, prev_weight_y, MBs


def algo7_ppo(prev_weight_x, prev_weight_y, flag, model, key_index):
    RNTI_x, CQI_x, BL_x, MB_x, RNTI_y, CQI_y, BL_y, MB_y = env.get_state() # to make get_metrics() to return backlogs as well

    if (flag == True): print("Metrics received from RAN: UE1(rnti,cqi,backlog): ", RNTI_x, CQI_x, BL_x,  " UE2(rnti,cqi,backlog): ", RNTI_y, CQI_y, BL_y)
    

    if (CQI_x > 0 and CQI_y > 0): 

        t0 = time.time()

        mb = 3000000 
        obs = torch.FloatTensor(([BL_x, CQI_x, mb, BL_y, CQI_y, mb])).unsqueeze(0).to(device)  # [BL1 CQI1 BL2 CQI2]
            
            
        with torch.no_grad():
                weights = np.clip(model.select_action(obs), a_min=0.0001, a_max=1.0).numpy()[0]
                new_weight_x = float(weights[0])
                new_weight_y = float(weights[1])
                weights = [RNTI_x, float(weights[0]),RNTI_y,float(weights[1])] 
        

        dt = time.time() - t0
        
        weights = [RNTI_x, new_weight_x, RNTI_y, new_weight_y]
        
        prev_weight_x = new_weight_x
        prev_weight_y = new_weight_y
        
    else:  weights = [RNTI_x, prev_weight_x, RNTI_y, prev_weight_y]
    
    return weights, prev_weight_x, prev_weight_y


def eval_loop(eval_episodes):
    test_data_dump = defaultdict(list)
    print("Starting Test Episodes..............")

    #PPO Policy
    print("\n\nPPO")
    PPOrewards = []
    PPOstalls = []
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
            action_v = agent.policy.select_action(state_var)[0].detach().cpu().numpy()
            
            
            action = int(action_v[0]) 
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

        print("\nNumber of stalls: ", stalls_episode , "\n")
        f_stalls.write(str(stalls_episode)+ "\n")
        
        
       
    df = pd.DataFrame(data=test_data_dump)
    df.to_csv(os.path.join(assets_dir(),'log_dir',f'{args.env_name}_{args.run_tag}','{}_ppo_test.csv'.format(args.env_name)))
    
    print(f"PPO -> mean={np.mean(PPOrewards)} std={np.std(PPOrewards)} total_stallsi={np.sum(PPOstalls)}")
    
use_gpu = False
device = (
    
    torch.device("cuda")
    if torch.cuda.is_available() and use_gpu
    else torch.device("cpu")
    
)

def eval_loop_model(eval_episodes):
    test_data_dump = defaultdict(list)
    print("Starting Test Episodes..............")

    # load the pre-trained model
    model = torch.load("../rl_model/model_demo.pt", map_location=torch.device('cpu'))
    model.to(device)
    model.eval()
    ###
    print(device)

    #PPO Policy
    print("\n\n PPO with pre-trained model")
    PPOrewards = []
    PPOstalls = []

    key_index = 0
    for i_episode in range(eval_episodes):
        state = env.reset()
        print('state',state, i_episode)
        if i_episode%10 == 0:
            print("state", state)
        reward_episode = 0
        stalls_episode = 0

        for _ in range(10000):

            #count stalls:
            MBs = state[0::2]
            for media_buffer in MBs:
                if media_buffer<=0:
                    stalls_episode += 1

            weights = [env.arm[0][0], 0.5, env.arm[0][4], 0.5]

            ##print(weights)

            t0 = time.time()
            state_var = tensor(state).unsqueeze(0).to(dtype).to(device)
            obs = torch.FloatTensor(([state[0], state[2], state[3], state[5]])).unsqueeze(0).to(device)  # [BL1 CQI1 BL2 CQI2]
            
            
            with torch.no_grad():
                weights = np.clip(model.select_action(obs), a_min=0.1, a_max=0.9).numpy()[0]
                weights = [env.arm[0][0], float(weights[0]),env.arm[0][4],float(weights[1])] 
            
            
            dt = time.time() - t0
            
            key_ran = "key_dt_"+str(key_index)
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
            redis_db.set(key_ran, str(dt)) 
            key_index = key_index +1 
            
            next_state, reward, done, _ = env.step_weights(weights)

            print(next_state)
            reward_episode += reward
            if done:
                break 
            state = next_state



def main_loop():
    time_init = time.time()

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
            data_dump['train_MB_avg'].append(log['MB_avg'])
            data_dump['train_BB_avg'].append(log['BB_avg'])
            data_dump['eval_MB_avg'].append(log_eval['MB_avg'])
            data_dump['eval_BB_avg'].append(log_eval['BB_avg'])
            writer.add_scalar(f'rewards/train_R_avg',log['avg_reward'],i_iter+1)
            writer.add_scalar(f'rewards/eval_R_avg',log_eval['avg_reward'],i_iter+1)
            writer.add_scalar(f'stalls/train',log['avg_stalls'],i_iter+1)
            writer.add_scalar(f'stalls/eval',log_eval['avg_stalls'],i_iter+1)
            writer.add_scalar(f'MB_avg/train',log['MB_avg'],i_iter+1)
            writer.add_scalar(f'BB_avg/train',log['BB_avg'],i_iter+1)
            writer.add_scalar(f'MB_avg/eval',log_eval['MB_avg'],i_iter+1)
            writer.add_scalar(f'BB_avg/eval',log_eval['BB_avg'],i_iter+1)

        if args.save_model_interval > 0 and (i_iter+1) % args.save_model_interval == 0:
            to_device(torch.device('cpu'), policy_net, value_net)
            os.makedirs( os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}'), exist_ok = True)
            pickle.dump((policy_net, value_net, running_state),
                        open(os.path.join(assets_dir(), 'learned_models',f'{args.env_name}_{args.run_tag}','{}_ppo.p'.format(args.env_name)), 'wb'))
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
timestamp = datetime.now()

env = multiArmRAN( seed=SEED, numEpisodes=numEpisodes,  Training=TRAIN, r1=789,  high_RB=789, low_RB=789, maxBufferSize=1000000, batchSize=5, episodeLimit=EPISODELIMIT, fixedSizeMDP=False, noiseVar=0, cost=0, zmq_params=None, numArms=2)
state_dim = env.observation_space.shape[0]
is_disc_action = len(env.action_space.shape) == 0
running_state = None

"""seeding"""
np.random.seed(SEED)
torch.manual_seed(SEED)

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

f_params = open("params_edgeric.txt")
line_algo = 0
lines = f_params.readlines()
idx_algos_str = lines[line_algo].split()
idx_algos = [eval(i) for i in idx_algos_str]
line_redis_server = 3
redis_db_1_ip = lines[line_redis_server]
f_params.close()

# REDIS server for ploting 
redis_db = redis.StrictRedis(host = 'localhost', port=6379, decode_responses = False, db=0)

# REDIS server for receiveing a pre-trained PPO model
if (len(redis_db_1_ip) > 1):
    redis_db_1 = redis.Redis(host = redis_db_1_ip, port=6379, decode_responses = False, db=0)
else:
    redis_db_1 = None

for idx_algo in idx_algos:
    print("algorithm: ", idx_algo)

    filename = "stalls_" + str(idx_algo) + ".txt"
    f_stalls = open(filename, "w")

    if(idx_algo <20):
        eval_loop_weight(args.max_iter_num, idx_algo)  ## testing for algos

    if(idx_algo == 20): # execute RL        
        eval_loop_model(args.max_iter_num)  ## evaluating the pre-trained model
