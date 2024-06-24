import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objs as go
'''
# Load the data from the CSV file into a Pandas dataframe
df = pd.read_csv("streamingtraindata.csv")

# Compute the mean and standard deviation of each row
means = df.mean(axis=1)
stddevs = df.std(axis=1)

# Create a new dataframe with the mean and standard deviation values
df_mean_stddev = pd.DataFrame({'mean': means, 'stddev': stddevs})

# Create a line plot of the means and add error bars for the standard deviations
#fig = px.line(df_mean_stddev, x=df_mean_stddev.index, y='mean', error_y='stddev', title='Training Curve')

fig = px.line(df_mean_stddev, x=df_mean_stddev.index, y='mean', title='Training Curve')
fig.add_shape(type='rect', x0=df_mean_stddev.index[0], x1=df_mean_stddev.index[-1],
              y0=means - stddevs, y1=means + stddevs, yref='y', xref='x',
              fillcolor='lightgray', opacity=0.2, layer='below', line_width=0)
fig.update_layout(xaxis_title="iteration", yaxis_title="reward: stalls")
# Show the plot
fig.show()
fig.write_image("training_curve.pdf")

import plotly.express as px
import pandas as pd
import numpy as np
'''
'''
# Load the data from the CSV file into a Pandas dataframe
df = pd.read_csv("cardrone_4ue_data.csv")

# Compute the mean and standard deviation of each row
#means = df.mean(axis=1)
#stddevs = df.std(axis=1)
means = df['reward_mean']
stddevs = df['reward_std']
trainsteps = df['train_step']

# Create a new dataframe with the mean and standard deviation values
#df_mean_stddev = pd.DataFrame({'mean': means, 'stddev': stddevs})

# Create a new dataframe with the mean and standard deviation values
df_train = pd.DataFrame({'reward_mean': means, 'reward_std': stddevs, 'train_step': trainsteps})

# Create a line plot of the means and add error bars for the standard deviations
#fig = px.line(df_mean_stddev, x=df_mean_stddev.index, y='mean', error_y='stddev', title='Training Curve')
#fig.update_layout(xaxis_title="iteration", yaxis_title="reward: Throughput [Mbps]")
# Show the plot
#fig.show()


fig_1 = go.Figure(
        [
            go.Scatter(
                name="Reward",
                x=df_train["train_step"],
                y=df_train["reward_mean"],
                mode="lines",
                line=dict(color="rgb(31, 119, 180)"),
            ),
            go.Scatter(
                name="mean+std",
                x=df_train["train_step"],
                y=df_train["reward_mean"] + df_train["reward_std"],
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="mean-std",
                x=df_train["train_step"],
                y=df_train["reward_mean"] - df_train["reward_std"],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode="lines",
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
                showlegend=False,
            ),
        ]
    )
fig_1.update_layout(
        yaxis_title="Throughput (Mbps)", title="Training Curve", hovermode="x"
    )
    
try:
        fig_1.show()
except:
        pass
    
fig_1.write_image("training_curve_4ue.pdf")

    # Save image to output dir
    #hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    #output_dir = hydra_cfg["runtime"]["output_dir"]
    #df_train.to_csv(os.path.join(output_dir, "training_curve.csv"))
    #fig_1.write_image(os.path.join(output_dir, "training_curve.pdf"))
    #fig_1.write_image("evaluation_curve.pdf")

'''

df = pd.read_csv("drone_on_rw_nodelay.csv")
epis = df['eval_episode']
agents = df['Agent']
rewards = df['reward']

df_eval = pd.DataFrame({'eval_episode': epis, 'reward': rewards, 'Agent': agents})

fig_2 = px.line(
        df_eval, x="eval_episode", y="reward", color="Agent", title="Evaluation"
    )
try:
        fig_2.show()
except:
        pass

fig_2.write_image("evaluation_curve_genz3.pdf")