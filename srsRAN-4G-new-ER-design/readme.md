### currently implemented

Metrics to send:  
CQI, SNR, UL pending Data  
tx_brate, rx_brate   

Control:  
UL blanking  
DL scheduling weights

TODO: CQI emulation in UE  
TODO: Add MCS for control  
TODO: TTI by TTI sync - (currently only RAN sends index, zmq in confalte everywhere)

### How to run the network 

#### Setup the core and srsenb in zmq mode
Terminal 1: Run the GRC broker, depending on the number of UEs {i}  
```bash
./top_block_{i}ue_23.04MHz.py
```
Terminal 2: Run the EPC 
update the hss section in the ./config/epc.conf to your file directory  
```bash
cd srsRAN_4G
./run_epc.sh
```

Terminal 3: Run the enb  
update ./config/enb.conf:    
the [rf] section for zmq/ uhd configurations  
[enb_files] section to your file directory    

```bash
cd srsRAN_4G
./run_enb.sh
```
#### Run the UEs 
Run UE1:  
```bash
cd srsRAN_4G/build
sudo ./srsue/src/srsue ../.config/ue1.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1
```
Run UE2: 
```bash
cd srsRAN_4G/build
sudo ./srsue/src/srsue ../.config/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2
```

To run automated scripts for {i} UEs:  
```bash
./run_srsran_{i}ue.sh
```

#### Stream Traffic:
check the folder /traffic_generator

#### Running EdgeRIC for downlink control:
check the folder /edgeric
