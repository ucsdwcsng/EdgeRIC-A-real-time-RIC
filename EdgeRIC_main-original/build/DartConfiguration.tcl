# This file is configured by CMake automatically as DartConfiguration.tcl
# If you choose not to use CMake, this file may be hand configured, by
# filling in the required variables.


# Configuration directories and files
SourceDirectory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main
BuildDirectory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build

# Where to place the cost data store
CostDataFile: 

# Site is something like machine.domain, i.e. pragmatic.crd
Site: wcsng23

# Build name is osname-revision-compiler, i.e. Linux-2.4.2-2smp-c++
BuildName: Linux-c++

# Subprojects
LabelsForSubprojects: 

# Submission information
SubmitURL: http://my.cdash.org/submit.php?project=srsRAN
SubmitInactivityTimeout: 

# Dashboard start time
NightlyStartTime: 00:00:00 GMT

# Commands for the build/test/submit cycle
ConfigureCommand: "/usr/local/lib/python3.8/dist-packages/cmake/data/bin/cmake" "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main"
MakeCommand: /usr/local/lib/python3.8/dist-packages/cmake/data/bin/cmake --build . --config "${CTEST_CONFIGURATION_TYPE}"
DefaultCTestConfigurationType: Release

# version control
UpdateVersionOnly: 

# CVS options
# Default is "-d -P -A"
CVSCommand: 
CVSUpdateOptions: 

# Subversion options
SVNCommand: 
SVNOptions: 
SVNUpdateOptions: 

# Git options
GITCommand: 
GITInitSubmodules: 
GITUpdateOptions: 
GITUpdateCustom: 

# Perforce options
P4Command: 
P4Client: 
P4Options: 
P4UpdateOptions: 
P4UpdateCustom: 

# Generic update command
UpdateCommand: 
UpdateOptions: 
UpdateType: 

# Compiler info
Compiler: /usr/bin/c++
CompilerVersion: 9.4.0

# Dynamic analysis (MemCheck)
PurifyCommand: 
ValgrindCommand: 
ValgrindCommandOptions: --error-exitcode=1 --trace-children=yes --leak-check=full --show-leak-kinds=all --track-origins=yes --show-reachable=yes --vex-guest-max-insns=25
DrMemoryCommand: 
DrMemoryCommandOptions: 
CudaSanitizerCommand: 
CudaSanitizerCommandOptions: 
MemoryCheckType: 
MemoryCheckSanitizerOptions: 
MemoryCheckCommand: MEMORYCHECK_COMMAND-NOTFOUND
MemoryCheckCommandOptions: 
MemoryCheckSuppressionFile: 

# Coverage
CoverageCommand: /usr/bin/gcov
CoverageExtraFlags: -l

# Testing options
# TimeOut is the amount of time in seconds to wait for processes
# to complete during testing.  After TimeOut seconds, the
# process will be summarily terminated.
# Currently set to 25 minutes
TimeOut: 1500

# During parallel testing CTest will not start a new test if doing
# so would cause the system load to exceed this value.
TestLoad: 

UseLaunchers: 
CurlOptions: 
# warning, if you add new options here that have to do with submit,
# you have to update cmCTestSubmitCommand.cxx

# For CTest submissions that timeout, these options
# specify behavior for retrying the submission
CTestSubmitRetryDelay: 5
CTestSubmitRetryCount: 3
