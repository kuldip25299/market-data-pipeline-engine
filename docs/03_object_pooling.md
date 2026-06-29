# Why Object Pooling?

Without pooling:

```
Allocate

↓

Use

↓

Destroy

↓

Allocate

↓

Destroy
```

This happens continuously.

Instead:

```
Pool

↓

Borrow Object

↓

Use

↓

Return Object

↓

Borrow Again
```

Only a small number of objects are created.

Everything else is reused.

Benefits:

- Lower memory allocation
- Better CPU cache locality
- Reduced Garbage Collection
- More predictable latency

This technique is common in:

- Trading systems
- Game engines
- Networking libraries
- Real-time simulations