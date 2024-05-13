# -*- coding: utf-8 -*-
"""
@author: vamsi tallam
"""

import pandas as pd
import random
import numpy as np

option = 6

"""
time     = 10
time_min = time
time_sec = time_min * 60
time_ms  = time_sec * 1000
"""

if option == 1:
    # cqi varies from 1 to 15 and goes from 15 to 1
    cqi1_low = 1
    cqi1_high = 15
    cqi2_low = 1
    cqi2_high = 15
    cqi_evol_freq = 2
    len_ = 1000

    cqi1 = []
    for i in range(len_):
        if i % 30 >= 1 and i % 30 <= 15:
            for _ in range(cqi_evol_freq):
                cqi1.append(i % 30)
        elif i % 30 > 15 and i % 30 < 29:
            for _ in range(cqi_evol_freq):
                cqi1.append(30 - i % 30)

    data = pd.concat([pd.Series(cqi1), pd.Series(cqi1)], axis=1)
    data.to_csv("data.csv", header=True, index=False)


if option == 2:
    # constant cqi for ue1 and ue2 respectively
    fixed_cqi1 = 15
    fixed_cqi2 = 5
    len_ = 1000

    cqi1 = pd.Series([fixed_cqi1 for _ in range(len_)])
    cqi2 = pd.Series([fixed_cqi2 for _ in range(len_)])

    data = pd.concat([cqi1, cqi2], axis=1)
    data.to_csv("data.csv", header=True, index=False)


if option == 3:
    # cqi varies in a given range
    cqi1_low = 8
    cqi1_high = 15
    cqi2_low = 1
    cqi2_high = 7
    cqi_evol_freq = 1
    len_ = 1000

    cqi1 = []
    cqi_range = 2 * (cqi1_high - cqi1_low) + 1
    for i in range(len_):
        if i % cqi_range >= 0 and i % cqi_range <= (cqi1_high - cqi1_low):
            for _ in range(cqi_evol_freq):
                cqi1.append(cqi1_low + i % cqi_range)
        elif i % cqi_range > (cqi1_high - cqi1_low) and i % cqi_range < cqi_range:
            for _ in range(cqi_evol_freq):
                cqi1.append(cqi1_high - (i % cqi_range - (cqi1_high - cqi1_low)))

    cqi2 = []
    cqi_range = 2 * (cqi2_high - cqi2_low) + 1
    for i in range(len_):
        if i % cqi_range >= 0 and i % cqi_range <= (cqi2_high - cqi2_low):
            for _ in range(cqi_evol_freq):
                cqi2.append(cqi2_low + i % cqi_range)
        elif i % cqi_range > (cqi2_high - cqi2_low) and i % cqi_range < cqi_range:
            for _ in range(cqi_evol_freq):
                cqi2.append(cqi2_high - (i % cqi_range - (cqi2_high - cqi2_low)))

    data = pd.concat([pd.Series(cqi1), pd.Series(cqi2)], axis=1)
    data.to_csv("data.csv", header=True, index=False)


if option == 4:
    # random cqi for ue1 and ue2 respectively
    cqi1_low = 1
    cqi1_high = 15
    cqi2_low = 1
    cqi2_high = 15
    len_ = 1000000

    cqi1 = pd.Series([random.randint(cqi1_low, cqi1_high) for _ in range(len_)])
    cqi2 = pd.Series([random.randint(cqi2_low, cqi2_high) for _ in range(len_)])

    data = pd.concat([cqi1, cqi2], axis=1)
    data.to_csv("data_random.csv", header=True, index=False)


if option == 5:
    # random walk cqi varies in a given range
    cqi1_low = 8
    cqi1_high = 15
    cqi1_walk = 2
    cqi2_low = 1
    cqi2_high = 7
    cqi2_walk = 2
    cqi_evol_freq = 1
    len_ = 1000

    cqi1 = []
    cqi = cqi1_low
    cqi1.append(cqi)
    for i in range(len_):
        curr_cqi = cqi + random.randint(cqi1_walk * -1, cqi1_walk)
        if curr_cqi <= cqi1_low:
            cqi = cqi1_low
            for _ in range(cqi_evol_freq):
                cqi1.append(cqi)
        elif curr_cqi >= cqi1_high:
            cqi = cqi1_high
            for _ in range(cqi_evol_freq):
                cqi1.append(cqi)
        else:
            cqi = curr_cqi
            for _ in range(cqi_evol_freq):
                cqi1.append(cqi)

    cqi2 = []
    cqi = cqi2_low
    cqi2.append(cqi)
    for i in range(len_):
        curr_cqi = cqi + random.randint(cqi2_walk * -1, cqi2_walk)
        if curr_cqi <= cqi2_low:
            cqi = cqi2_low
            for _ in range(cqi_evol_freq):
                cqi2.append(cqi)
        elif curr_cqi >= cqi2_high:
            cqi = cqi2_high
            for _ in range(cqi_evol_freq):
                cqi2.append(cqi)
        else:
            cqi = curr_cqi
            for _ in range(cqi_evol_freq):
                cqi2.append(cqi)



    data = pd.concat([pd.Series(cqi1), pd.Series(cqi2)], axis=1)
    data.to_csv("data_restrictedrandom.csv", header=True, index=False)

if option == 6:
    # random cqi for ue1 and ue2 respectively
    cqi1_low = 1
    cqi1_high = 15
    cqi2_low = 1
    cqi2_high = 15
    len_ = 1000000

    cqi1_one = [i for i in range(1, 16) for _ in range(2)] + [i for i in range(15, 0, -1) for _ in range(2)]
    cqi2_one = [i for i in range(15, 0, -1) for _ in range(2)]+ [i for i in range(1, 16) for _ in range(2)] 
    cqi1 = np.tile(cqi1_one, 1000)
    print(cqi1)
    cqi2 = np.tile(cqi2_one, 1000)


    data = pd.concat([pd.Series(cqi1), pd.Series(cqi2)], axis=1)
    data.to_csv("data_triangle.csv", header=True, index=False)