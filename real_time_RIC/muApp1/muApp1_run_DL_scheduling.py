###### This file reads from param_edgeric.txt to decide the scheduling algorithm
## update PF and RL models
import argparse
import os
import pickle
import sys
from collections import defaultdict
from datetime import datetime
from threading import Thread

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
from utils import *
import torch
import redis
from edgeric_agent import *



def eval_loop_weight(eval_episodes, idx_algo):
    
    key_index = 0
    
    for i_episode in range(eval_episodes):
        cnt = 0
        flag = True
        cnt_demo = 0
        key_algo = "algo"
        value_algo = "Half resource for each UE" # default algorithm
   
        if(idx_algo == 0):
            flag = False # to be deleted
            weights = fixed_weights(flag)
            send_scheduling_weight(weights,flag)
            value_algo = "Fixed Weights"

        # algo1 Max CQI       
        if(idx_algo == 1):
            weights = algo1_maxCQI_multi()
            send_scheduling_weight(weights,flag)
            value_algo = "MaxCQI"
    
        # algo2 Max Weight
        if(idx_algo == 2):
            weights = algo2_maxWeight_multi()
            send_scheduling_weight(weights,flag)
            value_algo = "MaxWeight"
        
        # algo3 PropFair
        if(idx_algo == 3):
            weights = algo3_propFair_multi(prev_weight_x, prev_weight_y, flag, f_stalls_timeseries) 
            rnti_weights, prev_weights, avg_CQIs = algo2_propFair_multi(prev_weights, avg_CQIs, flag)




            send_scheduling_weight(weights,flag)
            value_algo = "Proportional Fairness"
            
        if(flag == True):
            cnt = 0
            flag = False  

    #redis_db.set(key_algo, value_algo)   

def fixed_weights():
    ue_data = get_metrics_multi()
    numues = len(ue_data)
    weights = np.zeros(numues * 2)
    RNTIs = list(ue_data.keys())

    for i in range(numues):
        # Store RNTI and corresponding weight
        weights[i*2+0] = RNTIs[i]
        weights[i*2+1] = 1/numues
    
    return weights

                
def algo1_maxCQI_multi():
    ue_data = get_metrics_multi()
    numues = len(ue_data)
    weights = np.zeros(numues * 2)

    # Extract CQIs and RNTIs from ue_data
    CQIs = [data['CQI'] for data in ue_data.values()]
    RNTIs = list(ue_data.keys())

    if min(CQIs) > 0:  # Check if all CQIs are positive
        maxIndex = np.argmax(CQIs)
        new_weights = np.zeros(numues)
        
        high = 1 - ((numues - 1) * 0.1)
        low = 0.1
        for i in range(numues):
            if i == maxIndex:
                new_weights[i] = high
            else:
                new_weights[i] = low
            
            # Store RNTI and corresponding weight
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = new_weights[i]

        return weights
        
    else:  
        for i in range(numues):
        # Store RNTI and corresponding weight
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = 1/numues
            
        return weights

def algo2_maxWeight_multi():
    ue_data = get_metrics_multi()
    numues = len(ue_data)
    weights = np.zeros(numues * 2)
    # Extract CQIs and RNTIs and BLs from ue_data
    CQIs = [data['CQI'] for data in ue_data.values()]
    RNTIs = list(ue_data.keys())
    BLs = [data['Backlog'] for data in ue_data.values()]
    if (min(CQIs) > 0): 
        sum_CQI = np.sum(CQIs)
        sum_BL = np.sum(BLs) 
        if (sum_BL != 0):
            new_weights = CQIs/sum_CQI * BLs/sum_BL
            
        else:
            new_weights = CQIs/sum_CQI
   
        for i in range(numues):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = new_weights[i]
    
    else:  
         for i in range(numues):
            weights[i*2+0] = RNTIs[i]
            weights[i*2+1] = 1/numues
    
    return weights 

def algo3_propFair_multi(prev_weights, avg_CQIs, flag):
    ue_data = get_metrics_multi()
    numues = len(ue_data)
    weights = np.zeros(numues * 2)
    # Extract CQIs and RNTIs and BLs from ue_data
    CQIs = [data['CQI'] for data in ue_data.values()]
    RNTIs = list(ue_data.keys())
    BLs = [data['Backlog'] for data in ue_data.values()]

    if (min(CQIs)>0): 
        gamma = 0.1 
        if(avg_CQIs[0] == 0): avg_CQIs[0]=CQIs[0]
        if(avg_CQIs[1] == 0): avg_CQIs[1]=CQIs[1]
        
        
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

def eval_loop_model(num_episodes, out_dir):
    output_dir = out_dir 
    
    model = torch.load(os.path.join(output_dir, "model_demo.pt"), map_location=torch.device('cpu'))
    #model.to("cpu")
    model.eval()

    for episode in range(num_episodes):
        ue_data = get_metrics_multi()
        numues = len(ue_data)
        weight = np.zeros(numues * 2)
        # Extract CQIs and RNTIs and BLs from ue_data
        CQIs = [data['CQI'] for data in ue_data.values()]
        RNTIs = list(ue_data.keys())
        BLs = [data['Backlog'] for data in ue_data.values()]
        mbs = np.ones(numues)*300000

        obs = np.array(
                    [
                        param[ue]
                        for ue in range(numues)
                        for param in (BLs, CQIs, mbs)
                    ],
                    dtype=np.float32,
                )  # [BL1, CQI1, BL2, CQI2,.....]
            
        obs = torch.from_numpy(obs)
        obs = torch.unsqueeze(obs, dim=0)
            
        with torch.no_grad():
            
            action = model.select_action(obs)
            action = torch.squeeze(action)
        
        for ue in range(numues):

            percentage_RBG = action[ue] / sum(action)
            
            weight[ue*2+1] = percentage_RBG
            weight[ue*2] = RNTIs[ue]

        send_scheduling_weight(weight, True) 
    
#################
algorithm_mapping = {
    "Max CQI": 1,
    "Max Weight": 2,
    "Proportional Fair (PF)": 3,
    "Round Robin": 4,
    "RL": 20  # Adjust according to your specific algorithms and indices
}

rl_model_mapping = {
    "Initial Model": "../rl_model/initial_model",
    "Half Trained Model": "../rl_model/half_trained_model",
    "Fully Trained Model": "../rl_model/fully_trained_model"
}


# Establish a Redis connection (assuming Redis server is running locally)
redis_db = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# # REDIS server for ploting 
#redis_db = redis.StrictRedis(host = 'localhost', port=6379, decode_responses = False, db=0)

if __name__ == "__main__":

    while True:
        try:
            selected_algorithm = redis_db.get('scheduling_algorithm')
            if selected_algorithm:
                idx_algo = algorithm_mapping.get(selected_algorithm, None)

                if idx_algo is not None:
                    print("Algorithm index: ", idx_algo)
                    if idx_algo < 20:
                        eval_loop_weight(2000, idx_algo)  # For traditional scheduling algorithms
                    elif idx_algo == 20:  # For RL model execution
                        # Fetch the specific RL model from Redis
                        rl_model_name = redis_db.get('rl_scheduling_model')
                        if rl_model_name:
                            rl_model_path = rl_model_mapping.get(rl_model_name)
                            if rl_model_path:
                                print(f"Executing RL model at: {rl_model_path}")
                                eval_loop_model(2000, rl_model_path)
                            else:
                                print(f"Unknown RL model selected: {rl_model_name}")
                        else:
                            print("No RL model selected or RL model key does not exist in Redis.")
                else:
                    print("Unknown algorithm selected:", selected_algorithm)
            else:
                print("No algorithm selected or algorithm key does not exist in Redis.")
                
        except redis.exceptions.RedisError as e:
            print("Redis error:", e)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

                