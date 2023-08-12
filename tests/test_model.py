from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, OutOfStock, allocate

# ========================================================
#  Fixtures
# ========================================================


@pytest.fixture(scope="module")
def sku_red_tshirt_medium() -> str:
    return "RED-TSHIRT-MEDIUM"


@pytest.fixture(scope="module")
def sku_black_tshirt_large() -> str:
    return "BLACK-TSHIRT-LARGE"


@pytest.fixture(scope="module")
def today() -> date:
    return date.today()


@pytest.fixture(scope="module")
def tomorrow() -> date:
    return date.today() + timedelta(days=1)


@pytest.fixture(scope="module")
def later() -> date:
    return date.today() + timedelta(weeks=1)


# ========================================================
#  Tests
# ========================================================


def test_can_allocate_if_available_greater_than_required(sku_red_tshirt_medium):
    large_batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 4)
    assert large_batch.can_allocate(order_line)


def test_can_allocate_if_available_equals_required():
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    assert batch.can_allocate(order_line)


def test_cannot_allocate_if_available_smaller_than_required(sku_red_tshirt_medium):
    small_batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 15)
    assert not small_batch.can_allocate(order_line)


def test_cannot_allocate_returns_false_when_sku_does_not_match(
    sku_red_tshirt_medium, sku_black_tshirt_large
):
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_black_tshirt_large, 4)
    assert not batch.can_allocate(order_line)


def test_cannot_allocate_same_batch_twice(
    sku_red_tshirt_medium, sku_black_tshirt_large
):
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_black_tshirt_large, 1)
    assert not batch.can_allocate(order_line)


def test_allocation_successful(sku_red_tshirt_medium):
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines


def test_deallocate(sku_red_tshirt_medium):
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines

    batch.deallocate(order_line)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines


def test_deallocate_order_line_not_allocated_to_batch():
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines

    batch.deallocate(order_line)
    assert batch.available_quantity == 10
    assert order_line not in batch._allocated_order_lines


def test_allocation_is_idempotent(sku_red_tshirt_medium):
    batch = Batch("batch-001", sku_red_tshirt_medium, 10, date.today())
    order_line = OrderLine("order-001", sku_red_tshirt_medium, 10)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.available_quantity == 0
    assert order_line in batch._allocated_order_lines


def test_prefers_warehouse_stock_batches_to_batches_in_transit(
    sku_red_tshirt_medium, today
):
    warehouse_batch = Batch("warehouse-batch", sku_red_tshirt_medium, 10, None)
    transit_batch = Batch("transit-batch", sku_red_tshirt_medium, 10, today)
    order_line = OrderLine("order1", sku_red_tshirt_medium, 1)

    allocation = allocate(order_line, [warehouse_batch, transit_batch])

    assert allocation == "warehouse-batch"
    assert warehouse_batch.available_quantity == 9
    assert transit_batch.available_quantity == 10
    assert order_line in warehouse_batch._allocated_order_lines


def test_prefers_earlier_batches(sku_red_tshirt_medium, today, tomorrow, later):
    fast_batch = Batch("fast-batch", sku_red_tshirt_medium, 10, today)
    medium_batch = Batch("medium-batch", sku_red_tshirt_medium, 10, tomorrow)
    slow_batch = Batch("slow-batch", sku_red_tshirt_medium, 10, later)
    order_line = OrderLine("order1", sku_red_tshirt_medium, 1)

    allocation = allocate(order_line, [fast_batch, medium_batch, slow_batch])

    assert fast_batch.available_quantity == 9
    assert medium_batch.available_quantity == 10
    assert slow_batch.available_quantity == 10
    assert order_line in fast_batch._allocated_order_lines
    assert allocation == "fast-batch"


def test_raises_out_of_stock_error_if_cannot_allocate(sku_red_tshirt_medium, today):
    batch = Batch("fast-batch", sku_red_tshirt_medium, 10, today)
    order_line_1 = OrderLine("order1", sku_red_tshirt_medium, 10)
    allocate(order_line_1, [batch])

    with pytest.raises(OutOfStock, match=sku_red_tshirt_medium):
        order_line_2 = OrderLine("order2", sku_red_tshirt_medium, 1)
        allocate(order_line_2, [batch])
