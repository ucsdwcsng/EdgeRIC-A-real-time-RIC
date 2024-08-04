import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
from edgeric_messenger import *
import time  # Make sure time is imported

## before you import redis you have to install redis on your system by pip install redis
import redis

# Assuming get_metrics_multi() is defined correctly as before
# Initialize data structures
tx_values = {}
total_tx_sum = deque(maxlen=500)  # To track total Tx values for moving average calculation
total_tx_moving_average = []
kill = False
## To connect to a redis server
redis_db = redis.StrictRedis(host = 'localhost', port=6379, decode_responses = False, db=0)
redis_db.flushdb()

fig = plt.figure()
axs = fig.add_subplot(1,1,1)
x = [0]
y = [0]
ln , = plt.plot(x,y,'-')
max_y = 40 
plt.axis([0,100,0,max_y])
thrpt = 0

def initialize_ue_data(rnti):
    if rnti not in tx_values:
        tx_values[rnti] = deque(maxlen=1500)  # Deque for last 500 Tx values per RNTI

def update_tx_values(rnti, tx):
    if rnti not in tx_values:
        initialize_ue_data(rnti)
    tx_values[rnti].append(tx)
    #total_tx_sum.append(tx)  # Update the global tx sum for all RNTIs

def update_tx_sum_values(txsum):
    total_tx_sum.append(txsum)    

def calculate_total_moving_average():
    total_tx_moving_average.append(np.mean(total_tx_sum))

#def update(frame):
#    lines['Total'].set_data(range(len(total_tx_moving_average)), total_tx_moving_average)
#    axs.relim()
#    axs.autoscale_view()
#    return lines['Total'],

def data_fetching_thread():
    global kill, redis_db, thrpt, total_tx_sum, total_tx_moving_average ##, flag_request
    while True:
        ue_data = get_metrics_multi()
        #print(ue_data)
        tot = 0
        for rnti, data in ue_data.items():
            tx = data['Tx_brate']
            tx = tx*8.0/1000
            tot = tot + tx
            update_tx_values(rnti, tx)

        update_tx_sum_values(tot)    
        #thrpt = tot
        calculate_total_moving_average()
        #time.sleep(1)  # Simulate data fetching delay

def update(frame):
    global  thrpt, max_y, redis_db, total_tx_sum, total_tx_moving_average
    #print(thrpt)
    x.append(x[-1] +1)
    #y.append(thrpt)
    y.append(total_tx_moving_average[len(total_tx_moving_average)-1])
    plt.axis([0,len(x),0,max_y])
    ##algo = redis_db.get('algo')
    algo = "Default"
	#print(algo)
    if (algo == None): 
       algo = "b'Half resource for each UE'"
    plt.title('Total Tx Moving Average Across All RNTIs wuth Scheduler ' + str(algo).replace("b'", " : ").replace("'", ""))
    ##plt.title("Scheduler" + str(algo).replace("b'", " : ").replace("'", ""))
    ln.set_data(x,y)
    return ln, 

def main():
    global  thrpt, max_y, redis_db, total_tx_sum, total_tx_moving_average
    key_index_seq = 0 
    print('main')
    #fig, axs = plt.subplots(figsize=(10, 5))
    #fig.suptitle('Total Tx Moving Average Across All RNTIs')
    #lines = {'Total': axs.plot([], [], label='Total Tx Moving Average')[0]}
    ##axs.set_title('Total Tx Moving Average')
    #axs.set_xlabel('Time')
    #axs.set_ylabel('Tx_brate')
    #axs.legend()
    thread = threading.Thread(target=data_fetching_thread)
    thread.daemon = True
    thread.start()
    ani = FuncAnimation(fig, update, interval=100, save_count=500)
    plt.xlabel("Time [Sec]")
    plt.ylabel("Throughput [Mbps]")
    plt.tight_layout()
    plt.grid()
    plt.show()

if __name__ == "__main__":  
    main()