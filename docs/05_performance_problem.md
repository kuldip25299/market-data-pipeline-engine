# Chapter 5 — Finding the Performance Problem

## Business Motivation

A pipeline that works correctly at 10,000 ticks/sec but falls over at
1,000,000 ticks/sec is not "slow" in the abstract -- it is a business
risk. A busy trading day (earnings announcements, market open/close,
macro news) is exactly when tick volume spikes AND when strategies
most need timely data. This is precisely the wrong time for the
pipeline to become the bottleneck.

## Problem

We suspect the naive pipeline from Chapter 4 will slow down under real
load, but "I think it's slow" is not an engineering statement -- it's
a guess. We need to **prove** it, and more importantly, prove **why**.

## Naive (Wrong) Approach: Guessing

A common beginner mistake is to look at the code, spot something that
"seems slow" (often the `await` keywords, or the queue itself), and
start rewriting it -- without evidence. This wastes time and often
"optimizes" the wrong thing entirely.

## Why Guessing Fails

Python's performance characteristics are frequently unintuitive.
`asyncio` overhead is usually not the bottleneck people assume it is;
memory allocation patterns often are, especially under high object
churn. Without profiling, you cannot tell the difference.

## Production Solution: Profile First

We use Python's built-in `cProfile` to measure, not guess:

```bash
python -m cProfile -s cumulative benchmarks/benchmark_naive.py 1000000
```

Reading the output, sorted by cumulative time, reveals a large share
of total time attributable to:

- `Tick.__init__` (object construction) -- called once per tick, one
  million times in this run.
- The underlying memory allocator servicing those constructions.

This matches a well-known pattern in high-throughput Python systems:
**at high object-creation rates, allocation and garbage collection
overhead becomes a measurable, non-trivial fraction of total runtime**
-- even though a single allocation is extremely cheap in isolation.

## Confirming with `tracemalloc`

`PipelineMetrics` (see `market_pipeline/metrics.py`) already wraps
`tracemalloc` to report peak memory. Running the naive pipeline at
1,000,000 ticks shows peak memory scaling roughly linearly with tick
count -- direct evidence that we are allocating (and briefly holding)
one full object per tick, rather than reusing memory.

## The Bottleneck, Stated Precisely

> For every tick processed, the naive pipeline performs one Python
> object allocation (`Tick(...)`) that is discarded almost immediately
> after use. At high volumes, the cumulative cost of these
> allocations -- and the garbage collector work they generate --
> becomes a measurable fraction of total pipeline time and memory
> churn.

This -- and only this, because we've now shown evidence for it -- is
what we optimize in Chapter 6.

## Engineering Tradeoffs of Profiling Itself

- `cProfile` adds overhead to the run being measured, so its absolute
  numbers should not be quoted as "real" throughput -- only used to
  find *where* time goes, relatively. Chapter 7's benchmarks intentionally
  run WITHOUT the profiler attached, for accurate throughput numbers.

## Code

No pipeline code changes in this chapter -- only measurement tooling,
already present in `metrics.py`, applied against the existing naive
pipeline.

---

## What We Learned

- Never optimize based on intuition -- profile first, always.
- `cProfile` for CPU time, `tracemalloc` for memory, used together,
  give a fairly complete picture of where a Python program spends its
  resources.

## Key Takeaways

- The bottleneck we found (allocation overhead under high object
  churn) is a specific, well-understood, and fixable pattern -- not a
  vague "Python is slow."
- Profiling tools themselves add overhead; use them to find bottlenecks,
  not to report final performance numbers.

## Interview Questions

1. Why might `cProfile`'s reported total runtime be misleading if
   quoted as the system's real-world throughput?
2. What's the difference between what `cProfile` measures and what
   `tracemalloc` measures?

## Real Production Notes

Production systems facing this exact issue often reach for the same
solution introduced in Chapter 6 (object pooling), or move
allocation-heavy hot paths into a compiled extension (Cython, Rust via
PyO3) once pooling alone isn't enough. We stop at pooling in this
repository because it is the appropriate next step *for the bottleneck
we actually found* -- reaching for a rewrite in another language would
be a much larger, unjustified leap at this stage.

## Common Beginner Mistakes

- Profiling a tiny workload (e.g. 100 ticks) and concluding there's no
  bottleneck -- allocation overhead is a *volume*-dependent problem
  that only shows up at scale.
- Optimizing the first line of code that "looks slow" without profiler
  evidence.

## Exercises

1. Run `cProfile` against the naive pipeline at 10,000 ticks and then
   at 1,000,000 ticks. Compare the percentage of time attributed to
   `Tick.__init__` at each scale.
2. Try commenting out `metrics.record_queue_size()` calls -- does
   profiling show this as a meaningful cost? Why might tracking simple
   metrics be "cheap enough to always leave on" in production?
