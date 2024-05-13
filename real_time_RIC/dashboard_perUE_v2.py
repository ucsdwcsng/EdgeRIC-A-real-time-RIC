from collections import deque, defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import zmq
from edgeric_agent import *
import threading

# Initialize data structures
ue_metrics = defaultdict(lambda: defaultdict(deque))  # Stores raw values for all metrics
current_values = defaultdict(dict)  # Stores latest values for non-averaged metrics
moving_averages = defaultdict(dict)  # Stores moving averages for SNR and Tx

def initialize_ue_metrics(rnti, metrics):
    for metric in metrics:
        if metric in ['SNR', 'Tx'] and len(ue_metrics[rnti][metric]) == 0:
            ue_metrics[rnti][metric] = deque(maxlen=500)

def update_ue_metrics(rnti, metric, value):
    if metric in ['SNR', 'Tx']:
        ue_metrics[rnti][metric].append(value)
        moving_averages[rnti][metric] = np.mean(ue_metrics[rnti][metric])
    else:
        current_values[rnti][metric] = value  # Store latest value for CQI, Backlog, Pending Data

def data_fetching_thread():
    metrics = ['CQI', 'SNR', 'Backlog', 'Pending Data', 'Tx']
    while True:
        ue_data = get_metrics_multi()
        for rnti, metrics_dict in ue_data.items():
            initialize_ue_metrics(rnti, metrics)
            for metric, value in metrics_dict.items():
                update_ue_metrics(rnti, metric, value)
            if 'SNR' in moving_averages[rnti]:
                print(f'RNTI {rnti}, SNR Moving Avg: {moving_averages[rnti]["SNR"]}')
            if 'Tx' in moving_averages[rnti]:
                print(f'RNTI {rnti}, Tx Moving Avg: {moving_averages[rnti]["Tx"]}')

def update(frame):
    for rnti in moving_averages:  # Assumes RNTIs are present in moving_averages
        for metric in metrics:
            if metric in ['SNR', 'Tx'] and rnti in moving_averages and metric in moving_averages[rnti]:
                value = moving_averages[rnti][metric]
            elif metric in current_values[rnti]:
                value = current_values[rnti][metric]
            else:
                continue

            if rnti not in data or metric not in data[rnti]:
                data[rnti][metric] = []
                line, = axs[metrics.index(metric)].plot([], [], label=f'RNTI {rnti}')
                lines[metric][rnti] = line
                axs[metrics.index(metric)].legend()

            data[rnti][metric].append(value)
            lines[metric][rnti].set_data(range(len(data[rnti][metric])), data[rnti][metric])
            axs[metrics.index(metric)].relim()
            axs[metrics.index(metric)].autoscale_view()

    return [line for metric_lines in lines.values() for line in metric_lines.values()]

if __name__ == "__main__":
    metrics = ['CQI', 'SNR', 'Backlog', 'Pending Data', 'Tx']
    fig, axs = plt.subplots(5, 1, figsize=(10, 12))
    fig.suptitle('Live UE Metrics')
    
    lines = {metric: {} for metric in metrics}
    data = defaultdict(lambda: {metric: [] for metric in metrics})

    thread = threading.Thread(target=data_fetching_thread)
    thread.daemon = True
    thread.start()

    ani = FuncAnimation(fig, update, interval=100)
    plt.show()

