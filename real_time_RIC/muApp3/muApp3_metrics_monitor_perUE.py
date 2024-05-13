## View Live UE metrics #######


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import zmq
from edgeric_agent import *
import threading

# Initialize data structures
tx_values = {}
moving_averages = {}

def initialize_ue_data(rnti):
    if rnti not in tx_values:
        tx_values[rnti] = deque(maxlen=500)  # Deque for maintaining last 500 Tx values
        moving_averages[rnti] = 0 


def update_tx_values(rnti, tx):
    tx_values[rnti].append(tx)
    moving_averages[rnti] = np.mean(tx_values[rnti])  # Recompute the moving average

# Animation update function
# Animation update function
def update(frame):
    ue_data = get_metrics_multi()
    for rnti, metrics_dict in ue_data.items():
        if rnti not in data:
            data[rnti] = {metric: [] for metric in metrics}
            for metric in metrics:
                # Create a line for each RNTI and metric
                line, = axs[metrics.index(metric)].plot([], [], label=f'RNTI {rnti}')
                lines[metric][rnti] = line
                axs[metrics.index(metric)].legend()

        for metric, value in metrics_dict.items():
            data[rnti][metric].append(value)
            lines[metric][rnti].set_data(range(len(data[rnti][metric])), data[rnti][metric])
            axs[metrics.index(metric)].relim()  # Recalculate limits
            axs[metrics.index(metric)].autoscale_view()  # Autoscale

    return [line for metric_lines in lines.values() for line in metric_lines.values()]

def data_fetching_thread():
    while True:
        ue_data = get_metrics_multi()
        for rnti, data in ue_data.items():
            tx = data['Tx']
            initialize_ue_data(rnti)
            update_tx_values(rnti, tx)
            #print(f'RNTI {rnti}, Tx: {tx}, Moving Avg: {moving_averages[rnti]}')


if __name__ == "__main__":


    # Setup the figure and subplots
    fig, axs = plt.subplots(5, 1, figsize=(10, 12))  # 5 plots for 5 metrics
    fig.suptitle('Live UE Metrics')
    metrics = ['CQI', 'Backlog', 'SNR', 'Pending Data', 'Tx']

    # Initialize lines dictionary
    lines = {}
    for ax, metric in zip(axs, metrics):
        ax.set_title(metric)
        ax.set_xlabel('Time')
        ax.set_ylabel(metric)
        lines[metric] = {}


    # Initialize data storage for each RNTI and metric
    data = {}
    metrics = ['CQI', 'Backlog', 'SNR', 'Pending Data', 'Tx']
    thread = threading.Thread(target=data_fetching_thread)
    thread.daemon = True  # Set as a daemon so it will be killed when the main program exits
    thread.start()
    ani = FuncAnimation(fig, update, interval=100)  # Update every 1000 ms
    plt.show()

   


# # Start the animation
# ani = FuncAnimation(fig, update, interval=10)  # Update every 1000 ms
# plt.show()
