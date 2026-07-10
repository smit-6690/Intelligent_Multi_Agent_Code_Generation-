#pragma once

#include <cstddef>
#include <memory>
#include <mutex>
#include <vector>

namespace intellicode {

class MemoryPool {
public:
    MemoryPool(std::size_t block_size, std::size_t initial_blocks = 64);

    void* acquire();
    void release(void* pointer);
    std::size_t block_size() const noexcept;
    std::size_t capacity() const;
    std::size_t available() const;

private:
    void grow(std::size_t block_count);

    std::size_t block_size_;
    std::vector<std::unique_ptr<std::byte[]>> storage_;
    std::vector<void*> free_blocks_;
    mutable std::mutex mutex_;
};

}
