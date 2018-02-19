cmake_minimum_required(VERSION 3.6)
project(rpi-arcade-lights)

set(CMAKE_C_STANDARD 11)

set(SOURCE_FILES main.c)
add_executable(rpi-arcade-lights ${SOURCE_FILES})

find_library(config_LIB config)

target_link_libraries(rpi-arcade-lights ${config_LIB})