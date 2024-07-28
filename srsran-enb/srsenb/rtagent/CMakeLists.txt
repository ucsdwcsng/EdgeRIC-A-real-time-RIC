# # Create a library from the edgeric source files
# add_library(edgeric STATIC edgeric.cpp)

# # Include the current directory for header files
# target_include_directories(edgeric PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})


######################################3
set(SRCS
    edgeric.cpp
    metrics.pb.cc # Add the generated Protobuf source file
    scheduling_weights.pb.cc
)

add_library(edgeric STATIC ${SRCS})

# target_include_directories(edgeric PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_include_directories(edgeric PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ${PROTOBUF_INCLUDE_DIRS})


target_link_libraries(edgeric
    ${Boost_LIBRARIES}
    ${PROTOBUF_LIBRARIES}
    ${LIBCONFIGPP_LIBRARIES}
    ${SCTP_LIBRARIES}
)
########################################################################
# Disable specific warnings for Protobuf files
########################################################################
set_source_files_properties(metrics.pb.cc scheduling_weights.pb.cc PROPERTIES COMPILE_FLAGS -Wno-array-bounds)