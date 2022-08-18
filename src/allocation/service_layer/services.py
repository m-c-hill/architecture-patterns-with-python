from __future__ import annotations
from typing import Optional
from datetime import date

from src.allocation.domain import model
from src.allocation.domain.model import OrderLine
from src.allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass

class NoBatchAllocated(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(
    orderid: str, sku: str, qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref


def deallocate(order_id: str, sku: str, uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        try:
            batch = uow.batches.get_batch_with_allocated_order(order_id, sku)
        except IndexError:
            raise NoBatchAllocated(f"Order Line {order_id} has not been allocated to a branch.")
        batch.deallocate(order_id)
        uow.commit()
