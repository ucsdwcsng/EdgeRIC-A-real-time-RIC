# RT EdgeRIC

This is a Docker container version of EdgeRIC. There are several script files to build an image to run a Docker container of srsRAN-EdgeRIC including UHD and dependent packages. Inside the container, srsRAN and real-time RIC are executed. This branch can be used for an emulation for two UEs or an over-the-air experiment.

## Installing Docker Desktop (Ubuntu).
### 1. Set up Docker's apt repository.
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
### 2. Install the Docker packages.
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
### 3. Verify that the Docker Engine installation is successful by running the hello-world image.
```bash
sudo docker run hello-world
```

## Cloning a branch of srsRAN_Workshop_demo of EdgeRIC project.
```bash  
git clone https://github.com/ushasigh/EdgeRIC-A-real-time-RIC  
git checkout -b srsRAN_Workshop_demo 
```

## Building a Docker image of RT EdgeRIC.
### 1. Building a Docker image of UHD.
```bash
./dockerbuild_uhd.sh
```
### 2. Building a Docker image of RT EdgeRIC from UHD image.
```bash
./dockerbuild_edgeric.sh
```

## Running an RT EdgeRIC container.
```bash
./dockerrun_edgeric.sh host 0
```


### 1. Emulation of downlink resource allocation for two UEs. (Inside the container)
#### Terminal 1: Run GNU-Radio
```bash
 ./run_gnuradio.sh
```
#### Terminal 2: RUN EPC, eNB, UE1 and UE2
```bash
./dockerexec_edgeric.sh 0
cd srsran
./run_srsran.sh
```
Once all UEs are successfully connected to eNB, start iperf test by following the below.

#### Terminal 3: RUN iperf Server at UE1
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf server
```bash
./iperf_server_ue1.sh
```
#### Terminal 4: RUN iperf Client at UE1
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_server_ue1.sh
```
#### Terminal 5: RUN iperf Server at UE2
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf server
```bash
./iperf_server_ue2.sh
```
#### Terminal 6: RUN iperf Client at UE2
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_server_ue2.sh
```
When all UEs receive data, start a logging agent to visualize the total throughput of downlinks.
#### Terminal 7: RUN Logging Agent
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a logging agent
```bash
cd PyTorch-RL-Custom-demo
 ./run_logging.sh
```
#### Terminal 8: RUN RT EdgeRIC
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, open a RIC parametr file and select an algorithm for real-time resource allocation. 
```bash
cd PyTorch-RL-Custom-demo
nano examples/params_edgeric.txt
```
Once the parameter file is updated,  start an RT EdgeRIC
```bash
 ./run_rl.sh 1000 1
```












cd ../../EdgeRIC_main_ue2  
mkdir build  
cd build  
cmake ../  
make  
cd ../../EdgeRIC_main_ue3  
mkdir build  
cd build  
cmake ../  
make  
cd ../../EdgeRIC_main_ue4
mkdir build
cd build  
cmake ../  
make  
```
## Setup the 5G network
Depending on the number of UEs {i}, follow the steps:
### Start the network
Terminal 1:  
```bash
cd EdgeRIC_main
./top_block_{i}ue_23.04MHz.py
```

Terminal 2:  
```bash
cd EdgeRIC_main
./run_srsran_{i}ues.sh
```

### Starting iperf tarffic 
Terminal 3:  
```bash
cd EdgeRIC_main
./iperf_server_{i}ues.sh
```
Terminal 4:  
```bash
cd EdgeRIC_main
./iperf_client_{i}ues.sh <rate_ue{i}> <duration>, eg: ./iperf_client_2ues.sh 10M 10M 1000
```

## Run the Real Time RIC
Terminal 5:  

To inititate default scheduling (Max Weight):  
```bash
cd real_time_RIC  
./run_defaultscheduling.sh <{i}>, eg: ./run_deafultscheduling.sh 2 for 2 UEs    
```

To initiate training for RL agent:  
```bash
cd real_time_RIC  
./run_ppo.sh   
```
