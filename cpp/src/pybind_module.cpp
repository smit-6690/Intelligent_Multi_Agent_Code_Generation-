#include "intellicode/memory_pool.hpp"
#include "intellicode/runtime.hpp"

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(_native, module) {
    py::class_<intellicode::MetricSummary>(module, "MetricSummary")
        .def_readonly("count", &intellicode::MetricSummary::count)
        .def_readonly("mean_ms", &intellicode::MetricSummary::mean_ms)
        .def_readonly("p50_ms", &intellicode::MetricSummary::p50_ms)
        .def_readonly("p95_ms", &intellicode::MetricSummary::p95_ms)
        .def_readonly("p99_ms", &intellicode::MetricSummary::p99_ms)
        .def_readonly("throughput_per_second", &intellicode::MetricSummary::throughput_per_second);

    py::class_<intellicode::RuntimeResult>(module, "RuntimeResult")
        .def_readonly("outputs", &intellicode::RuntimeResult::outputs)
        .def_readonly("metrics", &intellicode::RuntimeResult::metrics);

    py::class_<intellicode::NativeRuntime>(module, "NativeRuntime")
        .def(py::init<std::size_t>(), py::arg("worker_count") = 0)
        .def("worker_count", &intellicode::NativeRuntime::worker_count)
        .def("map", [](intellicode::NativeRuntime& runtime,
                        const std::vector<std::string>& inputs,
                        const py::function& function) {
            return runtime.map(inputs, [&function](const std::string& input) {
                py::gil_scoped_acquire acquire;
                return function(input).cast<std::string>();
            });
        });

    py::class_<intellicode::MemoryPool>(module, "MemoryPool")
        .def(py::init<std::size_t, std::size_t>(), py::arg("block_size"), py::arg("initial_blocks") = 64)
        .def("block_size", &intellicode::MemoryPool::block_size)
        .def("capacity", &intellicode::MemoryPool::capacity)
        .def("available", &intellicode::MemoryPool::available);
}
