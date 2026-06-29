# System Architecture

The repository models a simplified version of a professional market data ingestion pipeline.

```mermaid
flowchart TD

Broker

↓

Producer

↓

Object Pool

↓

Async Queue

↓

Consumers

↓

Statistics
```

## Components

### Broker

Simulates a market data provider.

---

### Producer

Receives incoming market events.

---

### Object Pool

Reuses previously allocated Tick objects instead of allocating new ones.

---

### Queue

Buffers temporary bursts of market activity.

---

### Consumers

Process incoming events.

---

### Statistics

Measures throughput, latency and memory usage.