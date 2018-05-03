cmake_minimum_required(VERSION 3.10)
project(cs-proj)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-O3 -Wall -Wextra -pedantic -fdiagnostics-show-option")

set(PYTHON_LIBRARY C:/Users/pc/AppData/Local/Programs/Python/Python36-32/)

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

add_executable(cs-proj main.cpp bridge.c cy_stuff/cool_maths.c cy_stuff/very_cool_maths.c cy_stuff/heck.c)

if(WIN32)
    target_link_libraries(cs-proj "${PYTHON_LIBRARIES}/libs/libpython36.a")  # i guess only 3.6 is supported on windows
ELSE()
    target_link_libraries(cs-proj ${PYTHON_LIBRARIES})
ENDIF()