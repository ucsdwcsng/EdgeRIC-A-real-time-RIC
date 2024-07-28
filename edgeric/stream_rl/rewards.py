from stream_rl.registry import register_reward


@register_reward("default")
def default_reward(self, *, arg_1=None, arg_2=None, **kwargs):
    pass


@register_reward("throughput")
def throughput(total_bytes_transferred, backlog_lens, stalls):
    #return 8*total_bytes_transferred
    return total_bytes_transferred


@register_reward("negative_backlog_len")
def neg_bl(total_bytes_transferred, backlog_lens, stalls):
    return -1 * sum(backlog_lens)


@register_reward("stalls")
def stalls(total_bytes_transferred, backlog_lens, stalls):
    return stalls


@register_reward("SimpleCost")
def simple_cost(action, no_playout_previously, cost_params):
    backlog_action, playout_action = action
    r = cost_params["r"]
    c_1 = cost_params["c_1"]
    c_2 = cost_params["c_2"]
    lmbda_ = cost_params["lambda"]
    if not playout_action:
        cost = c_2 if no_playout_previously else c_1
    else:
        cost = -r * playout_action
    cost += lmbda_ * backlog_action**1.1
    return -1 * cost


@register_reward("Cost_1")
def cost1(beta_Ut, Y_t, V_t, cost_params):
    r = cost_params["r"]
    lmbda_ = cost_params["lambda"]
    cost = -r * beta_Ut if Y_t > 0 else 0
    cost += lmbda_ * V_t
    return -1 * cost
