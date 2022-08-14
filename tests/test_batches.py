from models import Batch, OrderLine
from datetime import date


def make_batch_and_order_line(sku: str, batch_qty: int, line_qty: int):
    """Helper function to create dummy batch and order line pairs for testing"""
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-001", sku, line_qty)
    )


# =========================
#  Tests
# =========================

def test_create_a_new_batch():
    batch = Batch(reference="batch-001", sku="RED-TABLE", available_quantity=10, eta=date(2020,8,12))
    assert batch.reference == "batch-001"
    assert batch.sku == "RED-TABLE"
    assert batch.available_quantity == 10
    assert batch.eta == date(year=2020, month=8, day=12)


def test_create_a_new_order_line():
    order_line = OrderLine(order_id="order-001", sku="RED-TABLE", quantity=5)
    assert order_line.order_id=="order-001"
    assert order_line.sku=="RED-TABLE"
    assert order_line.quantity==5


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
    batch = Batch(reference="batch-001", sku="RED-TABLE", quantity=10, eta=date(2020,8,12))
    order_line = OrderLine(order_id="order-001", sku="RED-CHAIRS", quantity=5)
    assert batch.can_allocate(order_line) is False


def test_cannot_allocate_same_order_line_twice():
    batch, order_line = make_batch_and_order_line("RED-CHAIRS", 10, 8)
    assert batch.can_allocate(order_line)
    assert batch.can_allocate(order_line) is False
