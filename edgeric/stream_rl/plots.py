import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import hydra
import os
import torch


def visualize_policy_cqi(model_dir=None):
    hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    output_dir = hydra_cfg["runtime"]["output_dir"]
    if not model_dir:
        model_dir = os.path.join(output_dir, "model_best.pt")
    model = torch.load(model_dir)
    model.to("cpu")
    model.eval()

    cqis = np.arange(16)
    allocated_RBG = np.zeros((16, 16))
    bl_1 = bl_2 = 150000
    for cqi_1 in cqis:
        for cqi_2 in cqis:
            obs = np.array([bl_1, cqi_1, bl_2, cqi_2], dtype=np.float32)
            obs = torch.from_numpy(obs)
            obs = torch.unsqueeze(obs, dim=0)
            with torch.no_grad():
                action = torch.squeeze(model.select_action(obs))
            action = np.clip(action, a_min=0.00000001, a_max=1.0)
            percentage_RBG = action[0] / sum(action)
            allocated_RBG[cqi_1][cqi_2] = int(percentage_RBG * 17)

    fig = go.Figure(data=[go.Surface(x=cqis, y=cqis, z=allocated_RBG)])
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.55, y=1.55, z=1.55),
    )
    fig.update_layout(
        title="Policy (CQI)",
        scene=dict(
            xaxis_title="UE1 CQI",
            yaxis_title="UE2 CQI",
            zaxis_title="Allocated RBGs",
        ),
        scene_camera=camera,
    )
    if not os.path.exists(os.path.join(output_dir, "policy_visualizations")):
        os.makedirs(os.path.join(output_dir, "policy_visualizations"))
    fig.write_image(os.path.join(output_dir, "policy_visualizations/policy_cqi.pdf"))
    fig.write_html(os.path.join(output_dir, "policy_visualizations/policy_cqi.html"))
    try:
        fig.show()
    except:
        pass


def visualize_policy_backlog_len(model_dir=None):
    hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    output_dir = hydra_cfg["runtime"]["output_dir"]
    if not model_dir:
        model_dir = os.path.join(output_dir, "model_best.pt")
    model = torch.load(model_dir)
    model.to("cpu")
    model.eval()
    step = 10000
    bls = np.arange(0, 300000 + step, step)
    allocated_RBG = np.zeros((len(bls), len(bls)))
    cqi_1 = cqi_2 = 150000
    for bl_1 in bls:
        for bl_2 in bls:
            obs = np.array([bl_1, cqi_1, bl_2, cqi_2], dtype=np.float32)
            obs = torch.from_numpy(obs)
            obs = torch.unsqueeze(obs, dim=0)
            with torch.no_grad():
                action = torch.squeeze(model.select_action(obs))
            action = np.clip(action, a_min=0.00000001, a_max=1.0)
            percentage_RBG = action[0] / sum(action)
            allocated_RBG[(bl_1 // step)][(bl_2 // step)] = int(percentage_RBG * 17)

    fig = go.Figure(data=[go.Surface(x=bls, y=bls, z=allocated_RBG)])
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.55, y=1.55, z=1.55),
    )
    fig.update_layout(
        title="Policy (Backlog len)",
        scene=dict(
            xaxis_title="UE1 Backlog",
            yaxis_title="UE2 Backlog",
            zaxis_title="Allocated RBGs",
        ),
        scene_camera=camera,
    )
    if not os.path.exists(os.path.join(output_dir, "policy_visualizations")):
        os.makedirs(os.path.join(output_dir, "policy_visualizations"))
    fig.write_image(os.path.join(output_dir, "policy_visualizations/policy_bl.pdf"))
    fig.write_html(os.path.join(output_dir, "policy_visualizations/policy_bl.html"))
    try:
        fig.show()
    except:
        pass


def visualize_edgeric_training(train_rewards):
    train_rewards = np.array(train_rewards)
    means = np.mean(train_rewards, axis=0)
    stds = np.std(train_rewards, axis=0)
    df_train = pd.DataFrame(
        list(zip(range(len(means)), means, stds)),
        columns=["train_step", "reward_mean", "reward_std"],
    )
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
    # Save image to output dir
    hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    output_dir = hydra_cfg["runtime"]["output_dir"]
    df_train.to_csv(os.path.join(output_dir, "training_curve.csv"))
    fig_1.write_image(os.path.join(output_dir, "training_curve.png"))
    #fig_1.write_image("evaluation_curve.pdf")


def visualize_edgeric_evaluation(
    ppo_agent_rewards, max_cqi_agent_rewards, max_pressure_agent_rewards
):

    df_eval = pd.DataFrame(
        list(
            zip(
                range(len(ppo_agent_rewards)),
                ppo_agent_rewards,
                max_pressure_agent_rewards,
                max_cqi_agent_rewards,
            )
        ),
        columns=["eval_episode", "PPO", "MaxWeight", "MaxCQI"],
    ).melt(
        id_vars=["eval_episode"],
        value_vars=["PPO", "MaxCQI", "MaxWeight"],
        var_name="Agent",
        value_name="reward",
    )
    fig_2 = px.line(
        df_eval, x="eval_episode", y="reward", color="Agent", title="Evaluation"
    )
    try:
        fig_2.show()
    except:
        pass
    # Save image to output dir
    hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    output_dir = hydra_cfg["runtime"]["output_dir"]
    df_eval.to_csv(os.path.join(output_dir, "evaluation_curve.csv"))
    fig_2.write_image(os.path.join(output_dir, "evaluation_curve.pdf"))
    



def plot_cdf(data):
    df_data = pd.DataFrame(data, columns=["forward_pass_time"])
    fig = px.ecdf(df_data, x="forward_pass_time")
    try:
        fig.show()
    except:
        pass
    # Save image to output dir
    hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
    output_dir = hydra_cfg["runtime"]["output_dir"]
    fig.write_image(os.path.join(output_dir, "fwd_pass_times.pdf"))


if __name__ == "__main__":
    #visualize_policy_cqi()
    df = pd.read_csv("streamingtraindata.csv")
    np_array = df.to_numpy()
    visualize_edgeric_training(np_array)
