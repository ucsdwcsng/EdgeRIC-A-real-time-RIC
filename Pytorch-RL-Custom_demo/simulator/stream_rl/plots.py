import numpy as np
import plotly.express as px
import pandas as pd


def visualize_policy(Pi):
    # Extract V_t,U_t for Y_t_2 == 0 i.e no stall previously
    Y_t_1_0, V_t_0, U_t_0 = np.where(Pi[:, 0, :, :] == 1)
    # Extract V_t,U_t for Y_t_2 == 1 i.e no playout previously
    Y_t_1_1, V_t_1, U_t_1 = np.where(Pi[:, 1, :, :] == 1)

    # Plotly plotting
    df_0 = pd.DataFrame(
        list(zip(Y_t_1_0, V_t_0, U_t_0)), columns=["Buffer length", "V_t", "U_t"]
    )
    df_1 = pd.DataFrame(
        list(zip(Y_t_1_1, V_t_1, U_t_1)), columns=["Buffer length", "V_t", "U_t"]
    )

    fig_1 = px.bar(
        df_0,
        x="Buffer length",
        y=["V_t", "U_t"],
        barmode="group",
        labels={"value": "No. of bytes", "variable": "Action"},
        title="No Stall Previously",
    )
    fig_2 = px.bar(
        df_1,
        x="Buffer length",
        y=["V_t", "U_t"],
        barmode="group",
        labels={"value": "No. of bytes", "variable": "Action"},
        title="Stalled Previously",
    )
    fig_1.show()
    fig_2.show()


def visualize_edgeric(
    train_rewards, ppo_agent_rewards, max_cqi_agent_rewards, max_pressure_agent_rewards
):
    df_train = pd.DataFrame(enumerate(train_rewards), columns=["train_step", "reward"])
    fig_1 = px.line(df_train, x="train_step", y="reward", title="Training Curve")

    df_eval = pd.DataFrame(
        list(
            zip(
                range(len(ppo_agent_rewards)),
                ppo_agent_rewards,
                max_pressure_agent_rewards,
                max_cqi_agent_rewards,
            )
        ),
        columns=["eval_episode", "ppo", "pressure", "cqi"],
    ).melt(
        id_vars=["eval_episode"],
        value_vars=["ppo", "cqi", "pressure"],
        var_name="agent_type",
        value_name="reward",
    )
    fig_2 = px.line(
        df_eval, x="eval_episode", y="reward", color="agent_type", title="Evaluation"
    )
    fig_1.show()
    fig_2.show()

def plot_cdf(data):
    df_data = pd.DataFrame(data,columns=["forward_pass_time"])
    fig = px.ecdf(df_data,x="forward_pass_time")
    fig.show()


if __name__ == "__main__":
    visualize_edgeric(
        [
            1,
            1,
            2,
            2,
            3,
            3,
        ],
        [2, 3],
        [1, 2],
        [3, 4],
    )
