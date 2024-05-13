# CMake generated Testfile for 
# Source directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/radio/test
# Build directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/radio/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(benchmark_radio_multi_rf "benchmark_radio" "-d" "zmq" "-a" "tx_port=tcp://*:2000,rx_port=tcp://localhost:2000;tx_port=tcp://*:2001,rx_port=tcp://localhost:2001;tx_port=tcp://*:2002,rx_port=tcp://localhost:2002;tx_port=tcp://*:2003,rx_port=tcp://localhost:2003;" "-p" "4")
set_tests_properties(benchmark_radio_multi_rf PROPERTIES  _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/radio/test/CMakeLists.txt;29;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/radio/test/CMakeLists.txt;0;")
add_test(test_radio_rt_gain_zmq "test_radio_rt_gain" "--srate=3.84e6" "--dev_name=zmq" "--dev_args=tx_port=ipc:///tmp/test_radio_rt_gain_zmq,rx_port=ipc:///tmp/test_radio_rt_gain_zmq,base_srate=3.84e6")
set_tests_properties(test_radio_rt_gain_zmq PROPERTIES  _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/radio/test/CMakeLists.txt;42;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/radio/test/CMakeLists.txt;0;")
