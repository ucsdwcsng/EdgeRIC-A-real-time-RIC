import sys
import os
import redis
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from edgeric_messenger import *
import time  # Make sure time is imported

redis_db = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

if __name__ == "__main__":
    t = 0
    
    while True:
        ue_dict, ran_index, ric_index = get_metrics_multi_monitor()
        #ue_dict = get_metrics_multi()
        
        output_policy = redis_db.get('RT-E2 Policy')
        # output_metrics = redis_db.get('RT-E2 Report')
        # time.sleep(0.5)
        # print(output_metrics)
        # print(output_policy)
        # ue_dict = get_metrics_multi()
        if (ran_index % 500 == 0): 
            print("RT-E2 Report: \n")
            print(f"RAN Index: {ran_index}, RIC index: {ric_index} \n")
            print(f"UE Dictionary: {ue_dict} \n")
            print(output_policy)
       
        
