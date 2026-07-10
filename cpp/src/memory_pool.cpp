#include "intellicode/memory_pool.hpp"

#include <algorithm>
#include <stdexcept>

namespace intellicode {

MemoryPool::MemoryPool(std::size_t block_size, std::size_t initial_blocks)
    : block_size_(std::max<std::size_t>(1, block_size)) {
    grow(std::max<std::size_t>(1, initial_blocks));
}

void* MemoryPool::acquire() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (free_blocks_.empty()) {
        grow(std::max<std::size_t>(1, storage_.size()));
    }
    void* pointer = free_blocks_.back();
    free_blocks_.pop_back();
    return pointer;
}

void MemoryPool::release(void* pointer) {
    if (pointer == nullptr) {
        return;
    }
    std::lock_guard<std::mutex> lock(mutex_);
    free_blocks_.push_back(pointer);
}

std::size_t MemoryPool::block_size() const noexcept {
    return block_size_;
}

std::size_t MemoryPool::capacity() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return storage_.size();
}

std::size_t MemoryPool::available() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return free_blocks_.size();
}

void MemoryPool::grow(std::size_t block_count) {
    storage_.reserve(storage_.size() + block_count);
    free_blocks_.reserve(free_blocks_.size() + block_count);
    for (std::size_t index = 0; index < block_count; ++index) {
        auto block = std::make_unique<std::byte[]>(block_size_);
        free_blocks_.push_back(block.get());
        storage_.push_back(std::move(block));
    }
}

}
