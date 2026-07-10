#include "intellicode/memory_pool.hpp"
#include "intellicode/runtime.hpp"
#include "intellicode/thread_pool.hpp"

#include <cassert>
#include <string>
#include <vector>

int main() {
    intellicode::ThreadPool pool(4);
    auto first = pool.submit([] { return 21; });
    auto second = pool.submit([](int value) { return value * 2; }, 21);
    assert(first.get() == 21);
    assert(second.get() == 42);
    pool.wait_idle();

    intellicode::MemoryPool memory(256, 2);
    void* block = memory.acquire();
    assert(block != nullptr);
    assert(memory.available() == 1);
    memory.release(block);
    assert(memory.available() == 2);

    intellicode::NativeRuntime runtime(2);
    const std::vector<std::string> inputs{"a", "bb", "ccc"};
    const auto result = runtime.map(inputs, [](const std::string& value) {
        return value + std::to_string(value.size());
    });
    assert(result.outputs.size() == 3);
    assert(result.outputs[0] == "a1");
    assert(result.outputs[2] == "ccc3");
    assert(result.metrics.count == 3);
    assert(result.metrics.throughput_per_second >= 0.0);
}
