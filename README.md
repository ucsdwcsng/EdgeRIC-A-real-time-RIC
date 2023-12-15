# EdgeRIC
## Installing srsRAN-EdgeRIC
### Install zmq
```bash  
git clone https://github.com/zeromq/libzmq.git  
cd libzmq  
./autogen.sh  
./configure  
make  
sudo make install  
sudo ldconfig
```

```bash  
git clone https://github.com/zeromq/czmq.git  
cd czmq  
./autogen.sh  
./configure  
make  
sudo make install  
sudo ldconfig  
```

### Install srsRAN supporting EdgeRIC messages and control
```bash  
git clone https://github.com/ushasigh/EdgeRIC-A-real-time-RIC  
cd EdgeRIC_main  
mkdir build  
cd build  
cmake ../  
make    
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
### Updating the config files on your system
Update the directory in files ./config/srsran/enb.conf and ./config/srsran/epc.conf  


    

### Start the network
Depending on the number of UEs {i}, follow the steps:  

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
