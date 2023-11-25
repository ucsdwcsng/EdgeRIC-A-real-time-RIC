import argparse
from cProfile import label
from collections import defaultdict

import os
import sys
import pickle
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import *
import matplotlib.pyplot as plt









def load_model(path):
    policy_net, value_net, running_state = pickle.load(open(path,'rb'))
    policy_net.eval()
    return policy_net

def get_actions(state_vector, policy_net):
    state_vector = [ torch.from_numpy(np.array([s])) for s in state_vector]
    policy_net.eval()
    action_probs = list(map(lambda x : policy_net.forward(x.unsqueeze(dim=0))[0].detach().numpy()[1],state_vector))
    return action_probs

def plot_thresh_policy(env_name, COSTS, run_tag):
    state_vector = np.linspace(0.0, 1.0, num=50)
    # print(state_vector)
    fig, axes = plt.subplots(nrows=1,ncols=1,figsize=(10,5),gridspec_kw={'wspace':0.13, 'hspace':0.0})
    for COST in COSTS:
        path_to_model = os.path.join(assets_dir(), 'learned_models',f'{env_name}_{run_tag}','{}_lambda{}_ppo.p'.format(env_name,COST))
        policy_net = load_model(path_to_model)
        action_probs = get_actions(state_vector,policy_net)
        axes.plot(state_vector,action_probs, label=f'lambda_{COST}')
        # print(action_probs)
    
    handles,labels = axes.get_legend_handles_labels()
    plt.legend(handles,labels)
    os.makedirs(os.path.join(assets_dir(),'policy_plots'),exist_ok=True)
    plt.savefig(os.path.join(assets_dir(),'policy_plots',f'thresh_{env_name}_{run_tag}.png'))


if __name__ == "__main__":
    COSTS = [  0.5, 0.75, 1.5, 3, 5 ]
    plot_thresh_policy("down_link_proto",COSTS)

    

