#
# Copyright 2013-2023 Software Radio Systems Limited
#
# This file is part of srsRAN
#
# srsRAN is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# srsRAN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# A copy of the GNU Affero General Public License can be found in
# the LICENSE file in the top-level directory of this distribution
# and at http://www.gnu.org/licenses/.
#

# set(SOURCES sched_base.cc sched_time_rr.cc sched_time_pf.cc)
# add_library(mac_schedulers OBJECT ${SOURCES})


################################## new stuff
# Add the source files to the mac_schedulers object library
set(SOURCES sched_base.cc sched_time_rr.cc sched_time_pf.cc)
add_library(mac_schedulers OBJECT ${SOURCES})

# Find ZeroMQ if the option is enabled
if(ENABLE_ZEROMQ)
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(ZeroMQ REQUIRED libzmq)

  # Include directories for ZeroMQ
  include_directories(${ZeroMQ_INCLUDE_DIRS})

  # Since mac_schedulers is an object library, it can't directly link libraries.
  # You must link ZeroMQ to the final target that includes this object library.
endif()



