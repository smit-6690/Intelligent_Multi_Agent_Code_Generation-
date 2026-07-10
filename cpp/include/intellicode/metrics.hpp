#pragma once

#include <chrono>
#include <cstddef>
#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>

namespace intellicode {

struct MetricSummary {
    std::size_t count{0};
    double mean_ms{0.0};
    double p50_ms{0.0};
    double p95_ms{0.0};
    double p99_ms{0.0};
    double throughput_per_second{0.0};
};

class MetricsCollector {
public:
    void record(const std::string& operation, double duration_ms);
    MetricSummary summary(const std::string& operation) const;
    void clear();

private:
    mutable std::mutex mutex_;
    std::unordered_map<std::string, std::vector<double>> samples_;
};

class ScopedTimer {
public:
    ScopedTimer(MetricsCollector& collector, std::string operation);
    ~ScopedTimer();

private:
    MetricsCollector& collector_;
    std::string operation_;
    std::chrono::steady_clock::time_point started_;
};

}
