# RT EdgeRIC

This is a Docker container version of EdgeRIC. There are several script files to build an image to run a Docker container of srsRAN-EdgeRIC including UHD and dependent packages. Inside the container, srsRAN and real-time RIC are executed. This branch can be used for an emulation or an over-the-air experiment for two UEs.

## A. Installing Docker Desktop (Ubuntu).
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

## B. Cloning a branch of srsRAN_Workshop_demo of EdgeRIC project.
```bash  
git clone https://github.com/ushasigh/EdgeRIC-A-real-time-RIC  
git checkout -b srsRAN_Workshop_demo 
```

## C. Building a Docker image of RT EdgeRIC.
### 1. Building a Docker image of UHD.
```bash
./dockerbuild_uhd.sh
```
### 2. Building a Docker image of RT EdgeRIC from UHD image.
```bash
./dockerbuild_edgeric.sh
```

## D. Running an RT EdgeRIC container.
```bash
./dockerrun_edgeric.sh host 0
```

### 1. Emulation of downlink resource allocation for two UEs. (Inside the container on one machine)
#### Terminal 1: Add namespace ue1 and ue2, and run GNU-Radio
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a GNU-Radio
```bash
./netns_setup.sh
 ./run_gnuradio.sh
```
#### Terminal 2: RUN EPC, eNB, UE1 and UE2
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a srsRAN
```bash
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
./iperf_server_ue1_netns.sh
```
#### Terminal 4: RUN iperf Client at eNB
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_client_ue1.sh
```
#### Terminal 5: RUN iperf Server at UE2
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf server
```bash
./iperf_server_ue2_netns.sh
```
#### Terminal 6: RUN iperf Client at eNB
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_client_ue2.sh
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
Once it is inside the container, open a RIC parameter file and select an algorithm for real-time resource allocation. 
```bash
cd PyTorch-RL-Custom-demo
nano examples/params_edgeric.txt
```
Once the parameter file is updated,  start an RT EdgeRIC
```bash
 ./run_rl.sh 1000 1
```


### 2. Over-the-air experiment of downlink resource allocation for two UEs. (Inside the containers on three machines)
Before running a Docker container, connect an USRP to each machine.

#### Machine 1: Run EPC, eNB
##### Terminal 1: 
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a EPC 
```bash
cd srsran
 ./epc.sh
```
##### Terminal 2: 
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start an eNB
```bash
cd srsran
 ./enb_usrp.sh
```
#### Machine 2: RUN UE1
##### Terminal 1: Build an image of vanilla version of srsRAN with additional packages
```bash
./dockerbuild_uhd_srsran.sh
./dockerbuild_uhd_srsran_packages.sh
```
Once the image is built, run a container of srsRAN 
```bash
./dockerrun_uhd_srsran.sh

```
Once it is inside the container, start UE as UE1
```bash
 cd build
 ./srsue/src/srsue
```
#### Machine 3: RUN UE2
##### Terminal 1: Build an image of vanilla version of srsRAN with additional packages
```bash
./dockerbuild_uhd_srsran.sh
./dockerbuild_uhd_srsran_packages.sh
```
Once the image is built, run a container of srsRAN 
```bash
./dockerrun_uhd_srsran.sh

```
Once it is inside the container, change imsi in /root/.config/srsran/ue.conf
```bash
nano /root/.config/srsran/ue.conf
```
Set the value of imsi (line 144) as 001010123456781 and save the file. 
Then, start UE as UE2
```bash
 cd build
 ./srsue/src/srsue
```


Once all UEs are successfully connected to eNB, start iperf test by following the below.

#### Machine 2 (UE1)
##### Terminal 2: RUN iperf Server 
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf server
```bash
iperf -s
```
#### Machine 1 (EPC, eNB)
##### Terminal 3: RUN iperf Client 
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_client_ue1.sh
```
#### Machine 3 (UE2)
##### Terminal 2: RUN iperf Server
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf server
```bash
iperf -s
```
#### Machine 1 (EPC, eNB)
##### Terminal 4: RUN iperf Client
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a iperf client
```bash
./iperf_client_ue2.sh
```
When all UEs receive data, start a logging agent to visualize the total throughput of downlinks.
##### Terminal 5: RUN Logging Agent
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, start a logging agent
```bash
cd PyTorch-RL-Custom-demo
 ./run_logging.sh
```
##### Terminal 6: RUN RT EdgeRIC
```bash
./dockerexec_edgeric.sh 0
```
Once it is inside the container, open a RIC parameter file and select an algorithm for real-time resource allocation. 
```bash
cd PyTorch-RL-Custom-demo
nano examples/params_edgeric.txt
```
Once the parameter file is updated,  start an RT EdgeRIC
```bash
 ./run_rl.sh 1000 1
```
