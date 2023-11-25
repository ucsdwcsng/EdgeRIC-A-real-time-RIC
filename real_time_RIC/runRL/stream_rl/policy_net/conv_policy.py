import numpy as np
import torch
import torch.nn as nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2

from stream_rl.registry import register_model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _coerce_torch(x):
    if isinstance(x, np.ndarray):
        x = np.array(list(x))  # .astype(np.float32)
        x = torch.from_numpy(x)
    return x


# Custom policy function
@register_model("conv_policy_net")
class ConvPolicyNet(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name
        )
        nn.Module.__init__(self)

        c = obs_space._shape[0]
        N = 4 * 2**4

        # Input: 1xCxHxW
        # Output = 1x|A|
        self.net = nn.Sequential(
            nn.Conv2d(c, N, kernel_size=5, stride=2),
            nn.LeakyReLU(),
            nn.Conv2d(N // 2**0, N // 2**1, kernel_size=5, stride=2, padding=2),
            nn.LeakyReLU(),
            nn.Conv2d(N // 2**1, N // 2**2, kernel_size=5, stride=2, padding=2),
            nn.LeakyReLU(),
            nn.Conv2d(N // 2**2, N // 2**3, kernel_size=5, stride=2, padding=2),
            nn.LeakyReLU(),
            nn.Conv2d(N // 2**3, N // 2**4, kernel_size=5, stride=2, padding=2),
            nn.AdaptiveAvgPool2d(1),
        )

        self.value_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(N // 2**4, N),
            nn.LeakyReLU(),
            nn.Linear(N, N // 2**4),
            nn.LeakyReLU(),
            nn.Linear(N // 2**4, 1),
            nn.Tanh(),
        )

        self.policy_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(N // 2**4, N),
            nn.LeakyReLU(),
            nn.Linear(N, N // 2**4),
            nn.LeakyReLU(),
            nn.Linear(N // 2**4, num_outputs),
            nn.Softmax(),  
        )

    def forward(self, input_dict, state, seq_lens):
        obs = _coerce_torch(input_dict["obs"]).float().to(device)

        y = self.net(obs)
        policy_logits = self.policy_head(y)
        self.value_raju = self.value_head(y)

        return policy_logits, state

    def value_function(self):
        assert self.value_raju is not None, "must call forward() first"
        return self.value_raju.reshape(-1)
