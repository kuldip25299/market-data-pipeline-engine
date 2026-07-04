# ADR 0002: Introduce an Object Pool for Tick Allocation

## Status
Accepted

## Context
Chapter 5's profiling (`cProfile` + `tracemalloc`) showed that, at high
tick volumes (500,000+ ticks/sec), a measurable share of total pipeline
time and peak memory was attributable to repeated allocation and
garbage collection of `Tick` objects, each of which is created and
discarded almost immediately after use.

## Decision
We introduce `TickObjectPool`, a fixed-size pool of pre-allocated,
reusable `Tick` objects, used by the optimized pipeline
(`pipeline_optimized.py`) in place of direct `Tick(...)` construction.

## Rationale
- This directly targets the specific, measured bottleneck from Chapter
  5 -- not a speculative one.
- `Tick.reset()` allows overwriting an existing object's fields
  without a new allocation, which is the mechanism the pool relies on.
- The pool falls back to real allocation when exhausted, preserving
  correctness even if sized incorrectly -- performance degrades
  gracefully rather than the system failing.

## Alternatives Considered
- **Do nothing**: rejected, since Chapter 5 provided clear profiling
  evidence of a real, scale-dependent cost.
- **Rewrite hot path in Cython/Rust**: would likely yield a larger
  performance improvement, but is a disproportionate response to the
  specific bottleneck identified, and would obscure the core lesson
  about allocation patterns for the target (beginner-to-intermediate)
  audience of this repository.
- **Use `__slots__` only, without pooling**: `Tick` already uses
  `__slots__` for baseline memory efficiency (see `models.py`), but
  this alone doesn't address the *repeated allocation* cost that
  pooling targets -- the two optimizations address different parts of
  the same underlying issue and are complementary.

## Consequences
- Callers must follow the `acquire()`/`release()` contract; failing to
  call `release()` silently degrades the pool's benefit over time
  (though it does not leak memory, since Python's GC still reclaims
  un-returned objects normally).
- Pooled objects are mutable and reused; code must never retain a
  reference to a `Tick` after releasing it. This tradeoff is
  documented explicitly in `docs/06_object_pool.md` and enforced only
  by convention and tests, not by the type system.
- This design assumes a single-process, single-consumer-group context;
  Chapter 8 discusses why this same mutable-pool approach does not
  extend cleanly to multi-consumer fan-out without an additional
  immutable-copy step.
