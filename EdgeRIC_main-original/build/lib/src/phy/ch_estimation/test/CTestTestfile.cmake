# CMake generated Testfile for 
# Source directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test
# Build directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/ch_estimation/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(chest_test_dl_cellid0 "chest_test_dl" "-c" "0")
set_tests_properties(chest_test_dl_cellid0 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;30;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_dl_cellid1 "chest_test_dl" "-c" "1")
set_tests_properties(chest_test_dl_cellid1 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;31;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_dl_cellid2 "chest_test_dl" "-c" "2")
set_tests_properties(chest_test_dl_cellid2 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;32;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_dl_cellid0_50prb "chest_test_dl" "-c" "0" "-r" "50")
set_tests_properties(chest_test_dl_cellid0_50prb PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;34;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_dl_cellid1_50prb "chest_test_dl" "-c" "1" "-r" "50")
set_tests_properties(chest_test_dl_cellid1_50prb PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;35;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_dl_cellid2_50prb "chest_test_dl" "-c" "2" "-r" "50")
set_tests_properties(chest_test_dl_cellid2_50prb PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;36;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_ul_cellid0 "chest_test_ul" "-c" "0" "-r" "50")
set_tests_properties(chest_test_ul_cellid0 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;49;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_ul_cellid1 "chest_test_ul" "-c" "1" "-r" "50")
set_tests_properties(chest_test_ul_cellid1 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;50;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_ul_cellid2 "chest_test_ul" "-c" "2" "-r" "50")
set_tests_properties(chest_test_ul_cellid2 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;51;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_6 "chest_test_srs" "-c" "2" "-r" "6")
set_tests_properties(chest_test_srs_6 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_15 "chest_test_srs" "-c" "2" "-r" "15")
set_tests_properties(chest_test_srs_15 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_25 "chest_test_srs" "-c" "2" "-r" "25")
set_tests_properties(chest_test_srs_25 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_50 "chest_test_srs" "-c" "2" "-r" "50")
set_tests_properties(chest_test_srs_50 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_75 "chest_test_srs" "-c" "2" "-r" "75")
set_tests_properties(chest_test_srs_75 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_srs_100 "chest_test_srs" "-c" "2" "-r" "100")
set_tests_properties(chest_test_srs_100 PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;61;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_nbiot_test_dl "chest_nbiot_test_dl")
set_tests_properties(chest_nbiot_test_dl PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;72;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(chest_test_sl_psbch "chest_test_sl")
set_tests_properties(chest_test_sl_psbch PROPERTIES  LABELS "lte;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;625;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;82;add_lte_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(dmrs_pdsch_test "dmrs_pdsch_test")
set_tests_properties(dmrs_pdsch_test PROPERTIES  LABELS "nr;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;634;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;92;add_nr_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(dmrs_pdcch_test_non_interleaved "dmrs_pdcch_test")
set_tests_properties(dmrs_pdcch_test_non_interleaved PROPERTIES  LABELS "nr;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;634;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;102;add_nr_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(dmrs_pdcch_test_interleaved "dmrs_pdcch_test" "-I")
set_tests_properties(dmrs_pdcch_test_interleaved PROPERTIES  LABELS "nr;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;634;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;103;add_nr_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(csi_rs_test "csi_rs_test" "-o" "3" "-S" "0" "-L" "150" "-f" "3" "-p" "15")
set_tests_properties(csi_rs_test PROPERTIES  LABELS "nr;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;634;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;113;add_nr_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
add_test(csi_rs_pattern_test "csi_rs_pattern_test")
set_tests_properties(csi_rs_pattern_test PROPERTIES  LABELS "nr;lib;phy;chest" _BACKTRACE_TRIPLES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/CMakeLists.txt;634;add_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;123;add_nr_test;/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/ch_estimation/test/CMakeLists.txt;0;")
