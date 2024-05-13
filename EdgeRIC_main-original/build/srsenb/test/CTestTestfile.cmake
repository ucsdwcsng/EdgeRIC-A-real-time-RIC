# CMake generated Testfile for 
# Source directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/srsenb/test
# Build directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/srsenb/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(enb_metrics_test "enb_metrics_test" "-o" "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/srsenb/test/enb_metrics.csv")
set_tests_properties(enb_metrics_test PROPERTIES  _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/srsenb/test/CMakeLists.txt;29;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/srsenb/test/CMakeLists.txt;0;")
subdirs("mac")
subdirs("phy")
subdirs("upper")
subdirs("rrc")
subdirs("s1ap")
