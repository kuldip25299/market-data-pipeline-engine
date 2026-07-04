# Chapter 1 — Introduction

## Business Motivation

Every trading strategy, from a retail investor's simple moving-average
crossover to a quantitative hedge fund's statistical arbitrage model,
depends on one thing above all else: **timely, accurate information
about prices**. Without market data, a strategy is blind. This
repository exists to answer, concretely and with working code, the
question every new quant infrastructure engineer eventually asks:

> "How does one stock price update from an exchange reach thousands of
> trading strategies with low latency?"

## Who This Is For

You know basic Python. You've probably never worked at a trading firm.
You've heard terms like "low latency" and "lock-free" thrown around
and want to actually understand them instead of nodding along. This
repository is written for you.

We will not assume you know what an object pool is, what backpressure
means, or why anyone would care about CPU cache locality. Every term
is defined in plain English, in the [glossary](glossary.md), the first
time it matters -- not before.

## What You Will Build

By the end of this repository you will have built, tested, and
benchmarked two versions of the same market data pipeline:

1. A **naive** version -- the version most engineers write first,
   using nothing but `asyncio.Queue` and plain object allocation.
2. An **optimized** version -- the same pipeline, rebuilt around an
   **Object Pool** after profiling proves exactly where the naive
   version's time goes.

You will also see *why* we stop there, and what a real production
system adds on top (multi-consumer fan-out, shared memory, sharding
across processes) -- covered conceptually in Chapter 9, even though
building all of it is outside the scope of a teaching repository.

## The Learning Path

```
Business Problem
      ↓
Real Trading Platform
      ↓
Market Data Flow
      ↓
Simple Pipeline
      ↓
Performance Bottlenecks
      ↓
Profiling
      ↓
Optimization
      ↓
Benchmarking
      ↓
Scaling
      ↓
Production Architecture
```

Each stage has its own chapter under `docs/`, and each chapter follows
the same structure: **Business Motivation → Problem → Naive Solution →
Why It Fails → Production Solution → Engineering Tradeoffs → Code.**

We optimize nothing until we've proven, with a profiler, that it's
worth optimizing. This is a deliberate choice, not an oversight --
premature optimization is one of the most common and most expensive
mistakes junior engineers make, and this repository is designed to
build the discipline to avoid it.

---

## What We Learned

- Market data pipelines exist to move price information from
  exchanges to the strategies that depend on it, as fast as
  correctness allows.
- This repository teaches the engineering journey, not just the final
  answer -- naive implementation first, optimization only after
  measurement.

## Key Takeaways

- "Why" always comes before "how" in this repository.
- Every optimization must be justified by a benchmark, not intuition.

## Interview Questions

1. Why might a trading system prefer nanosecond timestamps over
   millisecond timestamps?
2. What's wrong with optimizing code before measuring where time is
   actually spent?

## Real Production Notes

Real exchange feed handlers (e.g. NSE's NNF/NFCAST, NASDAQ's ITCH)
are binary protocols optimized for minimal parsing overhead -- very
different from the human-readable simulation used here. We simulate
in plain Python/dataclasses specifically so the *engineering patterns*
(pooling, queues, backpressure) are visible without protocol-parsing
noise.

## Common Beginner Mistakes

- Assuming "low latency" is a single number rather than a distribution
  (see `docs/glossary.md` under "Latency").
- Jumping straight to complex concurrency primitives before writing a
  correct, simple version first.

## Exercises

1. Before reading further, write down your own guess for how many
   ticks per second a busy exchange might generate for a single
   liquid stock. Compare it against real numbers you find later in
   this repository.
2. List three consumers of market data besides "trading strategies."
