from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(
        self, reference: str, sku: str, quantity: int, eta: Optional[date]
    ):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity
        self._allocated_order_lines = set()

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocated_order_lines:
            self._allocated_order_lines.remove(order_line)

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku and self.available_quantity >= order_line.quantity

    @property
    def allocated_quantity(self) -> int:
        return sum([order_line.quantity for order_line in self._allocated_order_lines])

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity
