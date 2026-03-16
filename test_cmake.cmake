cmake_minimum_required(VERSION 3.15)
set(CMAKE_POLICY_DEFAULT_CMP0091 NEW)

cmake_policy(GET CMP0091 POLICY_CMP0091)
if(NOT "${POLICY_CMP0091}" STREQUAL NEW)
    message(STATUS "Policy is not new! It is: '${POLICY_CMP0091}'")
endif()

project(MyProject)

cmake_policy(GET CMP0091 POLICY_CMP0091_POST)
message(STATUS "Policy post project is: '${POLICY_CMP0091_POST}'")
