from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(self, reference: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocated_order_lines = set()

    def __eq__(self, other) -> bool:
        if not other.isinstance(Batch):
            return False
        return self.reference == other.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        """assumes that a null eta is equivalent to today's date"""
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocated_order_lines.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocated_order_lines:
            self._allocated_order_lines.remove(order_line)

    def can_allocate(self, order_line: OrderLine) -> bool:
        return (
            self.sku == order_line.sku
            and self.available_quantity >= order_line.quantity
            and order_line not in self._allocated_order_lines
        )

    @property
    def allocated_quantity(self) -> int:
        return sum([order_line.quantity for order_line in self._allocated_order_lines])

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(
            batch for batch in sorted(batches) if batch.can_allocate(order_line)
        )
        batch.allocate(order_line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {order_line.sku}")


class OutOfStock(Exception):
    pass
