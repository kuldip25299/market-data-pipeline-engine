"""Unit tests for market_pipeline.object_pool."""

from market_pipeline.object_pool import TickObjectPool


def test_pool_preallocates_expected_count() -> None:
    pool = TickObjectPool(pool_size=10)
    assert pool.objects_created == 10
    assert pool.available_count == 10


def test_acquire_reuses_existing_objects() -> None:
    pool = TickObjectPool(pool_size=5)

    tick = pool.acquire(symbol="TCS", price=100.0, quantity=1, timestamp_ns=1)

    assert tick.symbol == "TCS"
    assert pool.objects_reused == 1
    assert pool.available_count == 4


def test_release_returns_object_to_pool() -> None:
    pool = TickObjectPool(pool_size=2)
    tick = pool.acquire(symbol="A", price=1.0, quantity=1, timestamp_ns=1)
    assert pool.available_count == 1

    pool.release(tick)
    assert pool.available_count == 2


def test_acquire_release_cycle_does_not_grow_pool_unbounded() -> None:
    pool = TickObjectPool(pool_size=3)

    for i in range(1000):
        tick = pool.acquire(symbol="A", price=float(i), quantity=1, timestamp_ns=i)
        pool.release(tick)

    # Correctness invariant: the pool never exceeds its configured size,
    # no matter how many acquire/release cycles run.
    assert pool.available_count == 3
    # Reuse should vastly outweigh creation once warmed up.
    assert pool.objects_reused == 1000


def test_pool_falls_back_to_allocation_when_exhausted() -> None:
    pool = TickObjectPool(pool_size=1)

    first = pool.acquire(symbol="A", price=1.0, quantity=1, timestamp_ns=1)
    second = pool.acquire(symbol="B", price=2.0, quantity=2, timestamp_ns=2)  # pool empty

    assert first is not second
    assert pool.objects_created == 2  # 1 preallocated + 1 overflow
    assert pool.available_count == 0
