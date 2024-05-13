# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.27

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/lib/python3.8/dist-packages/cmake/data/bin/cmake

# The command to remove a file.
RM = /usr/local/lib/python3.8/dist-packages/cmake/data/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build

# Include any dependencies generated for this target.
include lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/compiler_depend.make

# Include the progress variables for this target.
include lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/progress.make

# Include the compile flags for this target's objects.
include lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/flags.make

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/flags.make
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp.c
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/ccache /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o -MF CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o.d -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o -c /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp.c

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.i"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp.c > CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.i

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.s"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp.c -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.s

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/flags.make
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_tx.c
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building C object lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/ccache /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o -MF CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o.d -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o -c /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_tx.c

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.i"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_tx.c > CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.i

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.s"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_tx.c -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.s

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/flags.make
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_rx.c
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building C object lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/ccache /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o -MF CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o.d -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o -c /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_rx.c

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.i"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_rx.c > CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.i

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.s"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf/rf_zmq_imp_rx.c -o CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.s

# Object files for target srsran_rf_zmq
srsran_rf_zmq_OBJECTS = \
"CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o" \
"CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o" \
"CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o"

# External object files for target srsran_rf_zmq
srsran_rf_zmq_EXTERNAL_OBJECTS =

lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp.c.o
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_tx.c.o
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/rf_zmq_imp_rx.c.o
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/build.make
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/libsrsran_rf_utils.a
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/libsrsran_phy.a
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: /usr/local/lib/libzmq.so
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: /usr/lib/x86_64-linux-gnu/libfftw3f.so
lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1: lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Linking CXX shared library libsrsran_rf_zmq.so"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/srsran_rf_zmq.dir/link.txt --verbose=$(VERBOSE)
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && $(CMAKE_COMMAND) -E cmake_symlink_library libsrsran_rf_zmq.so.22.04.1 libsrsran_rf_zmq.so.0 libsrsran_rf_zmq.so

lib/src/phy/rf/libsrsran_rf_zmq.so.0: lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1
	@$(CMAKE_COMMAND) -E touch_nocreate lib/src/phy/rf/libsrsran_rf_zmq.so.0

lib/src/phy/rf/libsrsran_rf_zmq.so: lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1
	@$(CMAKE_COMMAND) -E touch_nocreate lib/src/phy/rf/libsrsran_rf_zmq.so

# Rule to build all files generated by this target.
lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/build: lib/src/phy/rf/libsrsran_rf_zmq.so
.PHONY : lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/build

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/clean:
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf && $(CMAKE_COMMAND) -P CMakeFiles/srsran_rf_zmq.dir/cmake_clean.cmake
.PHONY : lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/clean

lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/depend:
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : lib/src/phy/rf/CMakeFiles/srsran_rf_zmq.dir/depend

