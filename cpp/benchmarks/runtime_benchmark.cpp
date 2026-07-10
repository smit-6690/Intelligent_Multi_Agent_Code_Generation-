#include "intellicode/runtime.hpp"

#include <chrono>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    const std::size_t count = argc > 1 ? static_cast<std::size_t>(std::stoull(argv[1])) : 10000;
    std::vector<std::string> inputs(count, "generate-code");
    intellicode::NativeRuntime runtime;
    const auto started = std::chrono::steady_clock::now();
    const auto result = runtime.map(inputs, [](const std::string& value) {
        std::string output = value;
        for (int iteration = 0; iteration < 20; ++iteration) {
            output.append("-token");
        }
        return output;
    });
    const auto elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    std::cout << "tasks=" << count << '\n';
    std::cout << "workers=" << runtime.worker_count() << '\n';
    std::cout << "wall_seconds=" << elapsed << '\n';
    std::cout << "task_mean_ms=" << result.metrics.mean_ms << '\n';
    std::cout << "task_p99_ms=" << result.metrics.p99_ms << '\n';
    std::cout << "task_throughput_per_second=" << result.metrics.throughput_per_second << '\n';
}
