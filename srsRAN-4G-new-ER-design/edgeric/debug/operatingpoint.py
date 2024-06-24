# Quick and dirty code to help find optimal operating point for given tracefile
import pandas as pd
import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

cqi_map = {  # [Mean throughput, Std] (Mbps)
    0: [0, 0],
    1: [0.4432, 0.2206],
    2: [0.6394, 0.2047],
    3: [0.6990, 0.3575],
    4: [0.9112, 0.2882],
    5: [1.0014, 0.4647],
    6: [1.3261, 0.3873],
    7: [1.5028, 0.5879],
    8: [1.9077, 0.3314],
    9: [2.0347, 0.3120],
    10: [2.0542, 0.3142],
    11: [2.0479, 0.3019],
    12: [2.0517, 0.3086],
    13: [2.0303, 0.3170],
    14: [2.0239, 0.3053],
    15: [2.0477, 0.2942],
}


def operating_point(t=0.5): #(cqi_trace, t=0.5):
    #cqi_traces_df = pd.read_csv(cqi_trace)
    #cqi_traces = [cqi_traces_df.iloc[:, ue].tolist() for ue in range(2)]
    cqi_traces_1 = [15] * 60000#np.array(cqi_traces[0])
    cqi_traces_2 = [15] * 60000 #np.array(cqi_traces[1])
    throughput_1 = (
        np.average([cqi_map[cqi][0] for cqi in cqi_traces_1]) * 10000 * 17 #// 8
    )  # Convert to chunk_size per 10 TTI

    throughput_2 = (
        np.average([cqi_map[cqi][0] for cqi in cqi_traces_2]) * 10000 * 17 #// 8
    )

    operating_point_1 = throughput_1 * t
    operating_point_2 = throughput_2 * (1 - t)

    print(
        f"Chunk size to be fed every 10 TTIs, UE1 - {operating_point_1} bytes, UE2 {operating_point_2} bytes"
    )

    df = pd.DataFrame(
        dict(
            UE1_Mbps=np.array([throughput_1, operating_point_1, 0])
            * 800,  # Convert back to Mbps
            UE2_Mbps=np.array([0, operating_point_2, throughput_2]) * 800,
        )
    )

    df = df.sort_values(by="UE1_Mbps")
    fig = px.line(df, x="UE1_Mbps", y="UE2_Mbps", title="Operating Point")

    fig.add_traces(
        go.Scatter(
            x=np.array([operating_point_1]) * 800,
            y=np.array([operating_point_2]) * 800,
            mode="markers",
            name="Operating Point",
        )
    )
    fig.show()


if __name__ == "__main__":
    #operating_point("stream_rl/envs/cqi_traces/realistic.csv", t=0.2)
    operating_point(t=0.5)