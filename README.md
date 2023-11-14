# EdgeRIC_whittleIndex
## Installing srsRAN-EdgeRIC
### Install zmq
git clone https://github.com/zeromq/libzmq.git  
cd libzmq  
./autogen.sh  
./configure  
make  
sudo make install  
sudo ldconfig  

git clone https://github.com/zeromq/czmq.git  
cd czmq  
./autogen.sh  
./configure  
make  
sudo make install  
sudo ldconfig  

### Install srsRAN supporting EdgeRIC messages and control
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

## Setup the 5G network
Depending on the number of UEs {i}, follow the steps:
### Start the network
1. ./top_block_{i}ue_23.04MHz.py
2. ./run_srsran_{i}ues.sh

## Run the Real Time RIC
To inititate default scheduling:

### Starting iperf tarffic 
1. ./iperf_server_{i}ues.sh
2. ./iperf_client_{i}ues.sh <rate_ue{i}> <duration>, eg: ./iperf_client_2ues.sh 10M 10M 1000 
