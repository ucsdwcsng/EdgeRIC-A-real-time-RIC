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
include lib/examples/CMakeFiles/pdsch_ue.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include lib/examples/CMakeFiles/pdsch_ue.dir/compiler_depend.make

# Include the progress variables for this target.
include lib/examples/CMakeFiles/pdsch_ue.dir/progress.make

# Include the compile flags for this target's objects.
include lib/examples/CMakeFiles/pdsch_ue.dir/flags.make

lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o: lib/examples/CMakeFiles/pdsch_ue.dir/flags.make
lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/examples/pdsch_ue.c
lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o: lib/examples/CMakeFiles/pdsch_ue.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples && /usr/bin/ccache /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o -MF CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o.d -o CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o -c /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/examples/pdsch_ue.c

lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/pdsch_ue.dir/pdsch_ue.c.i"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/examples/pdsch_ue.c > CMakeFiles/pdsch_ue.dir/pdsch_ue.c.i

lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/pdsch_ue.dir/pdsch_ue.c.s"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/examples/pdsch_ue.c -o CMakeFiles/pdsch_ue.dir/pdsch_ue.c.s

# Object files for target pdsch_ue
pdsch_ue_OBJECTS = \
"CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o"

# External object files for target pdsch_ue
pdsch_ue_EXTERNAL_OBJECTS =

lib/examples/pdsch_ue: lib/examples/CMakeFiles/pdsch_ue.dir/pdsch_ue.c.o
lib/examples/pdsch_ue: lib/examples/CMakeFiles/pdsch_ue.dir/build.make
lib/examples/pdsch_ue: lib/src/phy/libsrsran_phy.a
lib/examples/pdsch_ue: lib/src/common/libsrsran_common.a
lib/examples/pdsch_ue: lib/src/phy/rf/libsrsran_rf.so.22.04.1
lib/examples/pdsch_ue: lib/src/support/libsupport.a
lib/examples/pdsch_ue: lib/src/srslog/libsrslog.a
lib/examples/pdsch_ue: /usr/lib/x86_64-linux-gnu/libmbedcrypto.so
lib/examples/pdsch_ue: /usr/lib/x86_64-linux-gnu/libsctp.so
lib/examples/pdsch_ue: lib/src/phy/rf/libsrsran_rf_utils.a
lib/examples/pdsch_ue: lib/src/phy/libsrsran_phy.a
lib/examples/pdsch_ue: /usr/lib/x86_64-linux-gnu/libfftw3f.so
lib/examples/pdsch_ue: lib/examples/CMakeFiles/pdsch_ue.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable pdsch_ue"
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/pdsch_ue.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
lib/examples/CMakeFiles/pdsch_ue.dir/build: lib/examples/pdsch_ue
.PHONY : lib/examples/CMakeFiles/pdsch_ue.dir/build

lib/examples/CMakeFiles/pdsch_ue.dir/clean:
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples && $(CMAKE_COMMAND) -P CMakeFiles/pdsch_ue.dir/cmake_clean.cmake
.PHONY : lib/examples/CMakeFiles/pdsch_ue.dir/clean

lib/examples/CMakeFiles/pdsch_ue.dir/depend:
	cd /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/examples /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/examples/CMakeFiles/pdsch_ue.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : lib/examples/CMakeFiles/pdsch_ue.dir/depend
