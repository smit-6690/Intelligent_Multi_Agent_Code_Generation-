#include "intellicode/runtime.hpp"

#include <thread>
#include <utility>

namespace intellicode {

NativeRuntime::NativeRuntime(std::size_t worker_count)
    : pool_(worker_count == 0 ? std::thread::hardware_concurrency() : worker_count) {}

RuntimeResult NativeRuntime::map(
    const std::vector<std::string>& inputs,
    const std::function<std::string(const std::string&)>& function) {
    metrics_.clear();
    std::vector<std::future<std::string>> futures;
    futures.reserve(inputs.size());
    for (const auto& input : inputs) {
        futures.push_back(pool_.submit([this, &function, input] {
            ScopedTimer timer(metrics_, "native_task");
            return function(input);
        }));
    }
    RuntimeResult result;
    result.outputs.reserve(futures.size());
    for (auto& future : futures) {
        result.outputs.push_back(future.get());
    }
    result.metrics = metrics_.summary("native_task");
    return result;
}

std::size_t NativeRuntime::worker_count() const noexcept {
    return pool_.worker_count();
}

}
