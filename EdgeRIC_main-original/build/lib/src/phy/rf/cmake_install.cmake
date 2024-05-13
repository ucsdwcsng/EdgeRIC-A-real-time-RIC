# Install script for directory: /home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/lib/src/phy/rf

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_uhd.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_uhd.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_uhd.so.22.04.1"
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_uhd.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_uhd.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_uhd.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHANGE
           FILE "${file}"
           OLD_RPATH "/usr/local/lib:"
           NEW_RPATH "")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_uhd.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_soapy.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_soapy.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_soapy.so.22.04.1"
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_soapy.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_soapy.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_soapy.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_soapy.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_zmq.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_zmq.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_zmq.so.22.04.1"
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_zmq.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_zmq.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf_zmq.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHANGE
           FILE "${file}"
           OLD_RPATH "/usr/local/lib:"
           NEW_RPATH "")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf_zmq.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "$ORIGIN/")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf.so.22.04.1"
    "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf.so.22.04.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libsrsran_rf.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHANGE
           FILE "${file}"
           OLD_RPATH "\$ORIGIN/:"
           NEW_RPATH "$ORIGIN/")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES "/home/wcsng-23/gitrepos/EdgeRIC-A-real-time-RIC/EdgeRIC_main/build/lib/src/phy/rf/libsrsran_rf.so")
endif()

