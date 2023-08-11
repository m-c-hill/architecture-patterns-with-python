from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    """
    Order lines contain a quantity of a specific product (identified by the product sku) associated
    with a given order.
    """

    order_id: str
    sku: str
    quantity: int


class Batch:
    """
    A batch is a quantity of a specific product to be ordered by the the purchasing department. A
    batch of stock is identified by a reference id. When a customer creates an order, the order
    lines associated with the order are allocated to a batch with a matching sku.
    """

    def __init__(self, reference: str, sku: str, eta: date, quantity: int):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._total_quantity = quantity
        self._allocated_order_lines: set[OrderLine] = set()

    def allocate(self, order_line: OrderLine) -> None:
        if self.can_allocate(order_line):
            self._allocated_order_lines.add(order_line)

    def deallocate(self, order_line: OrderLine) -> None:
        if order_line in self._allocated_order_lines:
            self._allocated_order_lines.remove(order_line)

    @property
    def allocated_quantity(self) -> int:
        return sum(order_line.quantity for order_line in self._allocated_order_lines)

    @property
    def available_quantity(self) -> int:
        return self._total_quantity - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return order_line.sku == self.sku and self.available_quantity >= order_line.quantity
