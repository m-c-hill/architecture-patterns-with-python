from datetime import date

from model import Batch, OrderLine

import pytest

# ========================================================
#  Fixtures
# ========================================================


@pytest.fixture(scope="module")
def sku_red_tshirt_medium() -> str:
    return "RED-TSHIRT-MEDIUM"


@pytest.fixture(scope="module")
def sku_black_tshirt_large() -> str:
    return "BLACK-TSHIRT-LARGE"


# ========================================================
#  Tests
# ========================================================


def test_can_allocate_if_available_greater_than_required(sku_red_tshirt_medium):
    large_batch = Batch("batch-001", sku_red_tshirt_medium, date.today(), 10)
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 4)
    assert large_batch.can_allocate(order_line)


def test_can_allocate_if_available_equals_required():
    batch = Batch(
        "batch-001", sku_red_tshirt_medium, date.today(), 10
    )
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    assert batch.can_allocate(order_line)


def test_cannot_allocate_if_available_smaller_than_required(sku_red_tshirt_medium):
    small_batch = Batch("batch-001", sku_red_tshirt_medium, date.today(), 10)
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 15)
    assert not small_batch.can_allocate(order_line)


def test_cannot_allocate_returns_false_when_sku_does_not_match(sku_red_tshirt_medium, sku_black_tshirt_large):
    batch = Batch("batch-001", sku_red_tshirt_medium, date.today(), 10)
    order_line = OrderLine("order-001", sku_black_tshirt_large, 4)
    assert not batch.can_allocate(order_line)


def test_cannot_allocate_same_batch_twice(
    sku_red_tshirt_medium, sku_black_tshirt_large
):
    batch = Batch("batch-001", sku_red_tshirt_medium, date.today(), 10)
    order_line = OrderLine("order-001", sku_black_tshirt_large, 1)
    assert not batch.can_allocate(order_line)


def test_allocation_successful(sku_red_tshirt_medium):
    batch = Batch(
        "batch-001", sku_red_tshirt_medium, date.today(), 10
    )
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines


def test_deallocate(sku_red_tshirt_medium):
    batch = Batch(
        "batch-001", sku_red_tshirt_medium, date.today(), 10
    )
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines

    batch.deallocate(order_line)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines


def test_deallocate_order_line_not_allocated_to_batch():
    batch = Batch(
        "batch-001", sku_red_tshirt_medium, date.today(), 10
    )
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines

    batch.deallocate(order_line)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines


def test_allocation_is_idempotent(sku_red_tshirt_medium):
    batch = Batch(
        "batch-001", sku_red_tshirt_medium, date.today(), 10
    )
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines
