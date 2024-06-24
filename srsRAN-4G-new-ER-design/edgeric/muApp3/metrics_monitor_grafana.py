# ## View Live UE metrics #######

# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import math
# import time
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import zmq
# from edgeric_agent import *
# import threading

# from influxdb import InfluxDBClient
# import time

# # Connect to InfluxDB
# client = InfluxDBClient(host='localhost', port=8086)
# client.create_database('uedata')
# client.switch_database('uedata')

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
# # Animation update function
# def update(frame):
#     ue_data = get_metrics_multi()
#     for rnti, metrics_dict in ue_data.items():
#         if rnti not in data:
#             data[rnti] = {metric: [] for metric in metrics}
#             for metric in metrics:
#                 # Create a line for each RNTI and metric
#                 line, = axs[metrics.index(metric)].plot([], [], label=f'RNTI {rnti}')
#                 lines[metric][rnti] = line
#                 axs[metrics.index(metric)].legend()

#         for metric, value in metrics_dict.items():
#             data[rnti][metric].append(value)
#             lines[metric][rnti].set_data(range(len(data[rnti][metric])), data[rnti][metric])
#             axs[metrics.index(metric)].relim()  # Recalculate limits
#             axs[metrics.index(metric)].autoscale_view()  # Autoscale

#     return [line for metric_lines in lines.values() for line in metric_lines.values()]

# def data_fetching_thread():
#     while True:
#         ue_data = get_metrics_multi()
#         for rnti, data in ue_data.items():
#             tx = data['Tx']
#             initialize_ue_data(rnti)
#             update_tx_values(rnti, tx)
            
#             # Prepare data in the format that InfluxDB expects
#             json_body = [
#                 {
#                     "measurement": "ue_metrics",
#                     "tags": {
#                         "RNTI": str(rnti)
#                     },
#                     "fields": {
#                         "Tx": tx,
#                         "Tx_Moving_Avg": moving_averages[rnti]['Tx'],
#                         "SNR": data.get('SNR', 0),  # Assume you fetch SNR similarly
#                         "SNR_Moving_Avg": moving_averages[rnti].get('SNR', 0)
#                     }
#                 }
#             ]
#             # Write data to InfluxDB
#             client.write_points(json_body)
#             time.sleep(1)  # Adjust based on your data rate



# if __name__ == "__main__":


#     # Setup the figure and subplots
#     fig, axs = plt.subplots(5, 1, figsize=(10, 12))  # 5 plots for 5 metrics
#     fig.suptitle('Live UE Metrics')
#     metrics = ['CQI', 'Backlog', 'SNR', 'Pending Data', 'Tx']

#     # Initialize lines dictionary
#     lines = {}
#     for ax, metric in zip(axs, metrics):
#         ax.set_title(metric)
#         ax.set_xlabel('Time')
#         ax.set_ylabel(metric)
#         lines[metric] = {}


#     # Initialize data storage for each RNTI and metric
#     data = {}
#     metrics = ['CQI', 'Backlog', 'SNR', 'Pending Data', 'Tx']
#     thread = threading.Thread(target=data_fetching_thread)
#     thread.daemon = True  # Set as a daemon so it will be killed when the main program exits
#     thread.start()
#     ani = FuncAnimation(fig, update, interval=100)  # Update every 1000 ms
#     plt.show()

   


# # # Start the animation
# # ani = FuncAnimation(fig, update, interval=10)  # Update every 1000 ms
# # plt.show()
   

############################### Only grafana

import sys
import os
import threading
import time
import numpy as np
from collections import deque
from influxdb import InfluxDBClient

# Configure path to import custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from edgeric_agent import get_metrics_multi  # Assuming this function fetches real-time data

# InfluxDB setup
try:
    client = InfluxDBClient(host='localhost', port=8086)
    client.create_database('uedata')
    client.switch_database('uedata')
except Exception as e:
    print(f"Failed to connect to InfluxDB: {e}")
    sys.exit(1)  # Exit if connection fails

# Data storage for metrics
tx_values = {}
moving_averages = {}

def initialize_ue_data(rnti):
    """ Initialize data structures for new RNTI. """
    if rnti not in tx_values:
        tx_values[rnti] = {'Tx': deque(maxlen=500), 'SNR': deque(maxlen=500)}
        moving_averages[rnti] = {'Tx': 0, 'SNR': 0}

def update_tx_values(rnti, metric, value):
    """ Update transmission values and compute moving averages for specified metric. """
    tx_values[rnti][metric].append(value)
    moving_averages[rnti][metric] = np.mean(tx_values[rnti][metric])

def data_fetching_thread():
    """ Thread to fetch and process data, then write to InfluxDB. """
    while True:
        try:
            ue_data = get_metrics_multi()
            for rnti, data in ue_data.items():
                if rnti not in tx_values:
                    initialize_ue_data(rnti)

                update_tx_values(rnti, 'Tx', data['Tx'])
                update_tx_values(rnti, 'SNR', data.get('SNR', 0))

                json_body = [
                    {
                        "measurement": "ue_metrics",
                        "tags": {"RNTI": str(rnti)},
                        "fields": {
                            "Tx": data['Tx'],
                            "Tx_Moving_Avg": moving_averages[rnti]['Tx'],
                            "SNR": data.get('SNR', 0),
                            "SNR_Moving_Avg": moving_averages[rnti]['SNR']
                        }
                    }
                ]
                client.write_points(json_body)
            time.sleep(1)  # Adjustable based on expected data update frequency
        except Exception as e:
            print(f"Error during data fetching or writing to InfluxDB: {e}")

if __name__ == "__main__":
    thread = threading.Thread(target=data_fetching_thread)
    thread.daemon = True
    thread.start()
    print("Data fetching thread started. Press Ctrl+C to stop.")
    try:
        while thread.is_alive():
            thread.join(1)
    except KeyboardInterrupt:
        print("Stopping data fetching...")
        sys.exit(0)
