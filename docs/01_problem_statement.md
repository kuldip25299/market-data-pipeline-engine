# Problem Statement

Professional trading platforms ingest millions of market events every second.

Every event must travel through multiple stages before reaching a trading strategy.

```
Broker

↓

Network

↓

Decoder

↓

Queue

↓

Trading Strategy
```

A beginner implementation usually creates a new Python object for every market tick.

```
tick = {
    "symbol": "...",
    "price": ...
}
```

This looks harmless.

Now imagine this happening two million times every second.

Python continuously allocates and destroys memory.

Eventually:

- Memory fragmentation increases
- CPU spends more time allocating objects
- Garbage Collection pauses become noticeable
- Throughput drops

The ingestion pipeline becomes the bottleneck instead of the trading algorithm.

This repository demonstrates how object reuse dramatically reduces this overhead.


#updated by kuldip