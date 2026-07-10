#pragma once

#include "intellicode/metrics.hpp"
#include "intellicode/thread_pool.hpp"

#include <cstddef>
#include <functional>
#include <string>
#include <vector>

namespace intellicode {

struct RuntimeResult {
    std::vector<std::string> outputs;
    MetricSummary metrics;
};

class NativeRuntime {
public:
    explicit NativeRuntime(std::size_t worker_count = 0);

    RuntimeResult map(
        const std::vector<std::string>& inputs,
        const std::function<std::string(const std::string&)>& function);

    std::size_t worker_count() const noexcept;

private:
    ThreadPool pool_;
    MetricsCollector metrics_;
};

}
