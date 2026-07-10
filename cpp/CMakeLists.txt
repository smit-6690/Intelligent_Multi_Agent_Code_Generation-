cmake_minimum_required(VERSION 3.20)
project(intellicode_native VERSION 1.0.0 LANGUAGES CXX)

option(INTELLICODE_BUILD_TESTS "Build native tests" ON)
option(INTELLICODE_BUILD_BENCHMARKS "Build native benchmarks" ON)
option(INTELLICODE_BUILD_PYTHON "Build pybind11 extension" OFF)

add_library(intellicode_native STATIC
    src/thread_pool.cpp
    src/memory_pool.cpp
    src/metrics.cpp
    src/runtime.cpp
)
target_include_directories(intellicode_native PUBLIC include)
target_compile_features(intellicode_native PUBLIC cxx_std_17)
set_target_properties(intellicode_native PROPERTIES POSITION_INDEPENDENT_CODE ON)

if(MSVC)
    target_compile_options(intellicode_native PRIVATE /W4 /permissive-)
else()
    target_compile_options(intellicode_native PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

if(INTELLICODE_BUILD_TESTS)
    enable_testing()
    add_executable(intellicode_native_tests tests/test_runtime.cpp)
    target_link_libraries(intellicode_native_tests PRIVATE intellicode_native)
    add_test(NAME intellicode_native_tests COMMAND intellicode_native_tests)
endif()

if(INTELLICODE_BUILD_BENCHMARKS)
    add_executable(intellicode_runtime_benchmark benchmarks/runtime_benchmark.cpp)
    target_link_libraries(intellicode_runtime_benchmark PRIVATE intellicode_native)
endif()

if(INTELLICODE_BUILD_PYTHON)
    find_package(pybind11 CONFIG REQUIRED)
    pybind11_add_module(_native src/pybind_module.cpp)
    target_link_libraries(_native PRIVATE intellicode_native)
    install(TARGETS _native LIBRARY DESTINATION intellicode/native)
endif()
