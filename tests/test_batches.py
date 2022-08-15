from datetime import date, timedelta

import pytest

from models import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = date.today() + timedelta(days=1)
later = date.today() + timedelta(days=7)


def make_batch_and_order_line(sku: str, batch_qty: int, line_qty: int):
    """Helper function to create dummy batch and order line pairs for testing"""
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-001", sku, line_qty),
    )


# =========================
#  Test models
# =========================


def test_create_a_new_batch():
    batch = Batch(
        reference="batch-001", sku="RED-TABLE", quantity=10, eta=date(2020, 8, 12)
    )
    assert batch.reference == "batch-001"
    assert batch.sku == "RED-TABLE"
    assert batch.available_quantity == 10
    assert batch.eta == date(year=2020, month=8, day=12)


def test_create_a_new_order_line():
    order_line = OrderLine(order_id="order-001", sku="RED-TABLE", quantity=5)
    assert order_line.order_id == "order-001"
    assert order_line.sku == "RED-TABLE"
    assert order_line.quantity == 5


# =============================
#  Test order line allocation
# =============================


def test_can_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 8)
    assert batch.can_allocate(order_line)


def test_can_allocate_if_available_exactly_equals_required():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 10)
    assert batch.can_allocate(order_line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 12)
    assert batch.can_allocate(order_line) is False


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch(
        reference="batch-001", sku="RED-TABLE", quantity=10, eta=date(2020, 8, 12)
    )
    order_line = OrderLine(order_id="order-001", sku="RED-CHAIRS", quantity=5)
    assert batch.can_allocate(order_line) is False


def test_deallocate_order_line_to_batch():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 2)
    batch.allocate(order_line)
    assert batch.available_quantity == 8
    batch.deallocate(order_line)
    assert batch.available_quantity == 10


def test_cannot_allocate_same_order_line_more_than_once():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 8)
    batch.allocate(order_line)
    batch.allocate(order_line)


# ==================================
#  Test batch preference allocation
# ==================================


def test_allocation_prefers_curent_stock_batches_to_shipments():
    # Order line allocation should prefer local in stock batches to batches being shipped
    in_stock_batch = Batch(
        reference="batch-in-stock", sku="RED-CHAIRS", quantity=100, eta=None
    )  # The local batch
    shipment_batch = Batch(
        reference="batch-shipment", sku="RED-CHAIRS", quantity=100, eta=later
    )  # The batch ready to be shipped
    order_line = OrderLine(order_id="order-001", sku="RED-CHAIRS", quantity=10)

    allocate(order_line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_allocation_prefers_batches_shipping_soonest():
    earliest_batch = Batch(
        reference="earliest-batch", sku="RED-CHAIRS", quantity=100, eta=today
    )
    middle_batch = Batch(
        reference="middle-batch", sku="RED-CHAIRS", quantity=100, eta=tomorrow
    )
    latest_batch = Batch(
        reference="latest-batch", sku="RED-CHAIRS", quantity=100, eta=later
    )
    order_line = OrderLine(order_id="order-001", sku="RED-CHAIRS", quantity=10)

    allocate(order_line, [earliest_batch, middle_batch, latest_batch])

    assert earliest_batch.available_quantity == 90
    assert middle_batch.available_quantity == 100
    assert latest_batch.available_quantity == 100


def test_allocation_returns_allocated_batch_ref():
    in_stock_batch = Batch(
        reference="batch-in-stock", sku="RED-CHAIRS", quantity=100, eta=None
    )
    shipment_batch = Batch(
        reference="batch-shipment", sku="RED-CHAIRS", quantity=100, eta=later
    )
    order_line = OrderLine(order_id="order-001", sku="RED-CHAIRS", quantity=10)

    allocated_batch_reference = allocate(order_line, [in_stock_batch, shipment_batch])

    assert allocated_batch_reference == in_stock_batch.reference


# ==================================
#  Test out of stock exception
# ==================================


def test_out_of_stock_exception_raised():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 10)
    allocate(order_line, [batch])

    with pytest.raises(OutOfStock, match="RED-CHAIRS"):
        second_order_line = OrderLine("order-782", "RED-CHAIRS", 1)
        allocate(second_order_line, [batch])
