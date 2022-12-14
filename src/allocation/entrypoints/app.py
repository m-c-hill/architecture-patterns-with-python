from datetime import datetime
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.allocation.domain import model
from src.allocation.adapters import orm
from src.allocation.service_layer import services, unit_of_work

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    try:
        order_id = request.json["orderid"]
        sku = request.json["sku"]
        services.deallocate(order_id, sku, unit_of_work.SqlAlchemyUnitOfWork())
    except services.NoBatchAllocated as e:
        return {"message": str(e)}, 400

    return {"orderid": order_id}, 200
