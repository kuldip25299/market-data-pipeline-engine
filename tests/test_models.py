"""Unit tests for market_pipeline.models."""

from market_pipeline.models import Tick


def test_tick_construction() -> None:
    tick = Tick(symbol="TCS", price=3500.5, quantity=10, timestamp_ns=123)
    assert tick.symbol == "TCS"
    assert tick.price == 3500.5
    assert tick.quantity == 10
    assert tick.timestamp_ns == 123
    assert tick.exchange == "SIM"  # default value


def test_tick_reset_mutates_in_place() -> None:
    tick = Tick(symbol="A", price=1.0, quantity=1, timestamp_ns=0)
    original_id = id(tick)

    tick.reset(symbol="B", price=2.0, quantity=2, timestamp_ns=99, exchange="NSE")

    assert id(tick) == original_id, "reset() must not allocate a new object"
    assert tick.symbol == "B"
    assert tick.price == 2.0
    assert tick.quantity == 2
    assert tick.timestamp_ns == 99
    assert tick.exchange == "NSE"


def test_tick_uses_slots() -> None:
    tick = Tick(symbol="A", price=1.0, quantity=1, timestamp_ns=0)
    assert not hasattr(tick, "__dict__"), "Tick should use __slots__ for memory efficiency"
