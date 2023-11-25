import torch
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


use_gpu = False
device = (
    torch.device("cuda")
    if torch.cuda.is_available() and use_gpu
    else torch.device("cpu")
)
print(device)


def main():
    #model = torch.load("rl_model/model_best.pt")
    model = torch.load("rl_model/model_best.pt", map_location=torch.device('cpu'))
    model.to(device)
    model.eval()

    for i in range(100):
        #obs = torch.tensor([[3570.0, 7.0, 0.0, 9.0]]).to(device)  # [BL1 CQI1 BL2 CQI2]
        #obs = torch.tensor([[100.0, 3.0, 100.0, 13.0]]).to(device)  # [BL1 CQI1 BL2 CQI2]
        cqis = [15, 2]
        obs = torch.tensor([[37500.0, cqis[0],37500.0*cqis[0], 37500.0, cqis[1],37500.0*cqis[1]]]).to(device)  # [BL1 CQI1 BL2 CQI2]
        with torch.no_grad():
            weights = np.clip(model.select_action(obs), a_min=0.0001, a_max=1.0)
        
        #cqis = obs[1::2]
        
        print('cqi',cqis)
        print(weights, np.eye(len(cqis))[np.argmax(cqis)])





if __name__ == "__main__":
    main()
