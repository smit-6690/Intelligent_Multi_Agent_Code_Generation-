#include "intellicode/metrics.hpp"

#include <algorithm>
#include <numeric>

namespace intellicode {
namespace {

double percentile(const std::vector<double>& values, double fraction) {
    if (values.empty()) {
        return 0.0;
    }
    const auto index = static_cast<std::size_t>((values.size() - 1) * fraction);
    return values[index];
}

}

void MetricsCollector::record(const std::string& operation, double duration_ms) {
    std::lock_guard<std::mutex> lock(mutex_);
    samples_[operation].push_back(duration_ms);
}

MetricSummary MetricsCollector::summary(const std::string& operation) const {
    std::vector<double> values;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        const auto iterator = samples_.find(operation);
        if (iterator == samples_.end()) {
            return {};
        }
        values = iterator->second;
    }
    std::sort(values.begin(), values.end());
    const double total = std::accumulate(values.begin(), values.end(), 0.0);
    MetricSummary result;
    result.count = values.size();
    result.mean_ms = total / static_cast<double>(values.size());
    result.p50_ms = percentile(values, 0.50);
    result.p95_ms = percentile(values, 0.95);
    result.p99_ms = percentile(values, 0.99);
    result.throughput_per_second = total > 0.0 ? values.size() * 1000.0 / total : 0.0;
    return result;
}

void MetricsCollector::clear() {
    std::lock_guard<std::mutex> lock(mutex_);
    samples_.clear();
}

ScopedTimer::ScopedTimer(MetricsCollector& collector, std::string operation)
    : collector_(collector), operation_(std::move(operation)), started_(std::chrono::steady_clock::now()) {}

ScopedTimer::~ScopedTimer() {
    const auto elapsed = std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now() - started_).count();
    collector_.record(operation_, elapsed);
}

}
