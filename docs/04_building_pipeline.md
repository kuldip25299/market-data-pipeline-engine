# Chapter 4 — Building the Simple Pipeline

## Business Motivation

We now have the mental model from Chapter 3. It's time to write real,
runnable code -- but still the simplest version that could possibly
work, with **no optimization**. Every senior engineer at every firm
listed at the top of this repository started exactly here on their
first working prototype.

## Problem

Turn the producer/consumer/queue diagram into working ``asyncio``
code that:

1. Generates a configurable number of simulated ticks.
2. Pushes them through a queue.
3. Processes each one on the consumer side.
4. Reports how long it took and how many ticks were handled.

## Naive Solution

See `market_pipeline/pipeline_naive.py` in full. The essential shape:

```python
async def _producer(queue, tick_count, metrics):
    async for tick in generate_ticks(tick_count):
        await queue.put(tick)
        metrics.ticks_generated += 1
    await queue.put(None)  # sentinel: "no more data"

async def _consumer(queue, metrics):
    while True:
        tick = await queue.get()
        if tick is None:
            break
        process_tick(tick)
        metrics.ticks_processed += 1

async def run_naive_pipeline(tick_count):
    queue = asyncio.Queue()
    await asyncio.gather(
        _producer(queue, tick_count, metrics),
        _consumer(queue, metrics),
    )
```

Notice what's absent: no object pooling, no multiple consumers, no
bounded queue size. This is intentional -- see the project-wide rule
in the root README: **never optimize before demonstrating a
bottleneck**.

## Why a Sentinel Value Instead of, Say, Cancelling a Task?

Cancelling an ``asyncio`` task mid-flight is more error-prone for
beginners (you have to handle `CancelledError` correctly, and it's
easy to leave the consumer in an inconsistent state). Pushing a
sentinel value (`None`) that means "stop" is a simple, well-understood
pattern that clearly communicates intent and is easy to reason about
when reading the code for the first time.

## Why It (Eventually) Fails

At low volumes (thousands of ticks), this implementation is completely
adequate -- there is no reason to add complexity here. But real
exchanges can produce **hundreds of thousands to millions of ticks per
second** for a full instrument universe. Chapter 5 runs this exact
pipeline at that scale and shows, with profiling data, exactly where
the time goes.

## Running It Yourself

```bash
python examples/run_naive_example.py
```

Expected output shape (real output shown below; your exact numbers
will vary by machine):

```
===================================================
               Naive Pipeline Example
===================================================
Ticks Generated       : 10,000
Ticks Processed       : 10,000
Objects Created       : 10,000
Objects Reused        : 0
Peak Queue Size       : 10,000
Elapsed Time          : 0.16 sec
Throughput            : 61,298 ticks/sec
Peak Memory           : 1.49 MB
===================================================
```

Notice `Peak Queue Size` equals the full tick count -- because this
queue is unbounded, the producer never waits for the consumer, so
every tick sits in the queue before being drained one by one. This is
an early, visible hint of the backpressure discussion in Chapter 6.

## Engineering Tradeoffs

- Simplicity over performance, deliberately, at this stage.
- Single producer / single consumer is easy to reason about but does
  not yet reflect "thousands of concurrent trading strategies" --
  that's addressed conceptually in Chapter 8.

## Code

Full implementation: `market_pipeline/pipeline_naive.py`
Supporting pieces: `market_pipeline/generator.py`, `models.py`,
`consumer.py`, `metrics.py`.

---

## What We Learned

- A correct, simple baseline is a prerequisite for any honest
  optimization work later.
- `asyncio.Queue` plus a sentinel value is a clean, beginner-friendly
  way to signal shutdown between coroutines.

## Key Takeaways

- Working code beats clever code, especially as a first draft.
- Every metric we'll later use to justify an optimization is being
  collected from day one (`PipelineMetrics`), not bolted on later.

## Interview Questions

1. Why use a sentinel value instead of an out-of-band signal (like a
   separate `asyncio.Event`) to indicate the producer is done?
2. What would happen to this pipeline if the consumer raised an
   exception on tick #500,000? How would you make it more robust?

## Real Production Notes

Real feed handlers almost always wrap the consumer loop in structured
exception handling and dead-letter queues so one malformed message
doesn't silently kill the entire pipeline -- something we intentionally
simplify away here to keep the core lesson visible.

## Common Beginner Mistakes

- Forgetting to `await` the sentinel `queue.put(None)`, causing the
  consumer to hang forever waiting for a shutdown signal that was
  never actually enqueued.
- Assuming `asyncio.gather` runs coroutines on separate threads (it
  does not -- they run cooperatively on a single event loop).

## Exercises

1. Modify `pipeline_naive.py` to print a running counter of ticks
   processed every 100,000 ticks.
2. What happens if you swap the order of arguments to `asyncio.gather`
   in `run_naive_pipeline`? Does the pipeline still work? Why or why
   not?
