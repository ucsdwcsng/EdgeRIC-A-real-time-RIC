
execute_process(
COMMAND git rev-parse --abbrev-ref HEAD
WORKING_DIRECTORY "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main"
OUTPUT_VARIABLE GIT_BRANCH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

execute_process(
COMMAND git log -1 --format=%h
WORKING_DIRECTORY "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main"
OUTPUT_VARIABLE GIT_COMMIT_HASH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Generating build_info.h")
configure_file(
  /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/include/srsran/build_info.h.in
  /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/include/srsran/build_info.h
)
