# Benchmarking

The repository contains two implementations.

## Version 1

Naive allocation

Creates a new Tick object for every event.

## Version 2

Object Pool

Reuses Tick objects.

Metrics collected:

- Total Execution Time
- Peak Memory
- Objects Created
- Objects Reused
- Queue Size
- Throughput

The goal is to understand *why* pooling improves performance rather than simply observing that it does.