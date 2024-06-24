## View Aggregate metrics - TO BE UPDATED #######
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import time

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import zmq
# import threading
# from collections import deque
# import numpy as np
# from edgeric_messenger import *

# # Initialize data structures
# tx_values = {}
# moving_averages = {}

# def initialize_ue_data(rnti):
#     if rnti not in tx_values:
#         tx_values[rnti] = deque(maxlen=500)  # Deque for maintaining last 500 Tx values
#         moving_averages[rnti] = 0 


# def update_tx_values(rnti, tx):
#     tx_values[rnti].append(tx)
#     moving_averages[rnti] = np.mean(tx_values[rnti])  # Recompute the moving average

# # Animation update function
# def update(frame):
#     for rnti in moving_averages:
#         if rnti not in data:
#             data[rnti] = []
#             line, = axs[0].plot([], [], label=f'RNTI {rnti}')  # Assuming Tx is the only metric plotted
#             lines['Tx'][rnti] = line
#             axs[0].legend()

#         data[rnti].append(moving_averages[rnti])
#         lines['Tx'][rnti].set_data(range(len(data[rnti])), data[rnti])
#         axs[0].relim()
#         axs[0].autoscale_view()

#     return [line for metric_lines in lines.values() for line in metric_lines.values()]

# def data_fetching_thread():
#     while True:
#         ue_data = get_metrics_multi()
#         for rnti, data in ue_data.items():
#             tx = data['Tx_brate']
#             initialize_ue_data(rnti)
#             update_tx_values(rnti, tx)
#             #print(f'RNTI {rnti}, Tx: {tx}, Moving Avg: {moving_averages[rnti]}')

# if __name__ == "__main__":
#     # Setup the figure and subplots
#     fig, axs = plt.subplots(2, 1, figsize=(6,4))  # 5 plots for 5 metrics
#     fig.suptitle('Aggregate Metrics')
#     metrics = ['Tx']

#     # Initialize lines dictionary
#     lines = {}
#     for ax, metric in zip(axs, metrics):
#         ax.set_title(metric)
#         ax.set_xlabel('Time')
#         ax.set_ylabel(metric)
#         lines[metric] = {}


#     # Initialize data storage for each RNTI and metric
#     data = {}
#     metrics = ['Tx']
#     thread = threading.Thread(target=data_fetching_thread)
#     thread.daemon = True  # Set as a daemon so it will be killed when the main program exits
#     thread.start()
#     ani = FuncAnimation(fig, update, interval=10)  # Update every 1000 ms
#     plt.show()

   
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
from edgeric_messenger import *
import time  # Make sure time is imported

# Assuming get_metrics_multi() is defined correctly as before

# Initialize data structures
tx_values = {}
total_tx_sum = deque(maxlen=500)  # To track total Tx values for moving average calculation
total_tx_moving_average = []

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

def update(frame):
    lines['Total'].set_data(range(len(total_tx_moving_average)), total_tx_moving_average)
    axs.relim()
    axs.autoscale_view()
    return lines['Total'],

def data_fetching_thread():
    while True:
        ue_data = get_metrics_multi()
        tot = 0
        for rnti, data in ue_data.items():
            tx = data['Tx_brate']
            tx = tx*8.0/1000
            tot = tot + tx
            update_tx_values(rnti, tx)
        update_tx_sum_values(tot)    
        calculate_total_moving_average()
        #time.sleep(1)  # Simulate data fetching delay

if __name__ == "__main__":
    fig, axs = plt.subplots(figsize=(10, 5))
    fig.suptitle('Total Tx Moving Average Across All RNTIs')
    lines = {'Total': axs.plot([], [], label='Total Tx Moving Average')[0]}
    axs.set_title('Total Tx Moving Average')
    axs.set_xlabel('Time')
    axs.set_ylabel('Tx_brate')
    axs.legend()

    thread = threading.Thread(target=data_fetching_thread)
    thread.daemon = True
    thread.start()

    ani = FuncAnimation(fig, update, interval=10, save_count=500)
    plt.show()


