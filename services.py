from __future__ import annotations

import model
from model import OrderLine, Batch
from repository import AbstractRepository
from datetime import date
from typing import Optional, List


class InvalidSku(Exception):
    pass

class NoBatchAllocated(Exception):
    pass

def is_valid_sku(sku: str, batches: List[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session
) -> None:
    batch = Batch(ref, sku, qty, eta)
    repo.add(batch)
    session.commit()


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(line: OrderLine, repo: AbstractRepository, session) -> None:
    batch = [b for b in repo.list() if b.sku == line.sku and b.order_line_assigned_to_batch(line)]
    if not batch:
        raise NoBatchAllocated(f"Order Line {line.orderid} has not been allocated to a branch.")
    batch[0].deallocate(line)
    session.commit()
