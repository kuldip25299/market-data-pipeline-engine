# ADR 0001: Use asyncio for the Pipeline's Concurrency Model

## Status
Accepted

## Context
The pipeline must handle concurrent, independent activities: receiving
(or simulating) incoming market data while simultaneously processing
already-received ticks. Python offers several concurrency options:
`threading`, `multiprocessing`, and `asyncio`.

## Decision
We use `asyncio` for the producer/consumer pipeline built in this
repository.

## Rationale
- The pipeline's core workload (in a real system) is I/O-bound --
  waiting on network sockets for the next exchange message -- which is
  exactly the workload `asyncio` is designed to handle efficiently on
  a single thread, without the overhead of OS-level context switching
  between threads.
- `asyncio.Queue` provides a simple, well-understood hand-off point
  between coroutines that mirrors the producer/consumer pattern used
  throughout real distributed systems, making it an excellent teaching
  vehicle.
- `threading` would introduce the Global Interpreter Lock (GIL) as a
  source of confusion for beginners without providing genuine
  parallelism for I/O-bound work.
- `multiprocessing` would solve CPU-bound parallelism (relevant to
  Chapter 8's scaling discussion) but adds serialization and IPC
  complexity that isn't needed to teach the core pipeline patterns
  covered in Chapters 1-7.

## Consequences
- CPU-bound consumer work (e.g. a computationally heavy strategy)
  would still block the single-threaded event loop; this repository's
  simulated `process_tick` is intentionally lightweight to keep this
  out of scope. Chapter 8 discusses moving to multiple processes when
  this becomes a real constraint.
- All code in this repository assumes a single event loop; there is no
  cross-process safety story implemented here (see Chapter 9).
