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


# TODO: rework with unit of work
def deallocate(order_id: str, uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        line = uow.orders.get(order_id)
        batch = uow.orders.get_batch()  # [b for b in uow.batches.list() if b.sku == line.sku and b.order_line_assigned_to_batch(line)]
        if not batch:
            raise NoBatchAllocated(f"Order Line {line.orderid} has not been allocated to a branch.")
        batch.deallocate(line)
        uow.commit()
