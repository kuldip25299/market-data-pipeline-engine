# Chapter 2 — The Real World Problem

## Business Motivation

Before writing a single line of pipeline code, we need to understand
who produces market data, who consumes it, and why the journey between
them is an engineering problem at all -- not just a network request.

## Who Generates Market Data

**Exchanges** (NSE, NYSE, NASDAQ, CME, Binance) are marketplaces where
buyers and sellers submit orders. Every time an order is placed,
modified, cancelled, or matched (traded), the exchange emits an event.
Multiply this by thousands of instruments and millions of participants,
and a single busy exchange can emit **millions of events per second**
across its full instrument universe.

## Who Consumes Market Data

- **Trading strategies** -- algorithms that decide whether to buy,
  sell, or hold, based on incoming prices.
- **Risk engines** -- systems that monitor exposure and can halt
  trading if limits are breached.
- **Order engines** -- systems that translate a strategy's decision
  into an actual order sent back to the exchange.
- **Human traders** -- via dashboards, charts, and order books.
- **Compliance and audit systems** -- which record everything for
  regulatory review.

## Why Strategies Depend On It

A strategy is, at its core, a function of market data: `decision =
f(current_price, historical_prices, order_book_state, ...)`. If the
data arrives late, the decision is made on stale information -- in a
fast-moving market, this can mean buying at a price that no longer
exists. If data is lost or duplicated, the strategy's internal state
becomes wrong, sometimes silently. Correctness and speed are not
"nice to have" here; they are the entire value proposition of the
system.

## The Real-World Journey of One Price Update

```
NSE
  ↓
Broker (co-located server / market data vendor)
  ↓
WebSocket / TCP feed
  ↓
Market Data Pipeline  <-- this repository
  ↓
Strategies (thousands, potentially)
  ↓
Risk Engine
  ↓
Order Engine
  ↓
Broker
  ↓
Exchange
```

Walking through each step:

1. **NSE**: A trade executes on the exchange. A tick is generated.
2. **Broker**: Brokers (or specialized market data vendors) receive
   the exchange's raw feed and often normalize/re-broadcast it to
   their clients.
3. **WebSocket/TCP feed**: The transport layer carrying bytes from the
   broker's infrastructure to yours.
4. **Market Data Pipeline**: Our focus. This layer receives raw feed
   events, decodes them into a usable structure (our `Tick`), and
   distributes them internally to every interested consumer.
5. **Strategies**: React to the tick -- update internal state, maybe
   decide to trade.
6. **Risk Engine**: Before any order goes out, exposure/limits are
   checked.
7. **Order Engine**: Converts an approved decision into an exchange
   order message.
8. **Broker → Exchange**: The order travels back out, completing the
   loop.

This entire round trip, in competitive trading environments, is
measured in **microseconds to low milliseconds**. Our pipeline is just
one link in that chain -- but if it's slow, every downstream link
inherits the delay.

## Why This Repository Focuses on the Pipeline, Not the Whole Chain

Building a full trading system (strategy engine, risk engine, order
routing, exchange connectivity) is a multi-year effort at a real firm.
This repository deliberately scopes down to the **market data
pipeline** step -- the part responsible for ingesting and distributing
data internally -- because it is self-contained, teachable, and
contains nearly every core distributed-systems concept (producers,
consumers, queues, backpressure, memory management) in miniature.

---

## What We Learned

- Market data pipelines sit in the middle of a larger, latency-
  sensitive chain -- their job is fast, correct internal distribution.
- Multiple, very different consumers (strategies, risk, compliance)
  all depend on the same underlying tick stream.

## Key Takeaways

- Speed matters because stale data leads to bad decisions, not just
  because "faster is better" in the abstract.
- Correctness (no lost/duplicated ticks) is just as important as raw
  speed.


## Real Production Notes

Many firms pay for **co-location** -- placing their servers physically
inside or near the exchange's data center -- specifically to shave
microseconds off steps 1-3 above, before the pipeline even begins.

## Common Beginner Mistakes

- Believing "the exchange" and "the pipeline" are the same thing --
  they are separate systems with separate responsibilities.
- Underestimating how many independent consumers a single tick may
  need to reach.

