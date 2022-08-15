import uuid
import pytest
import requests

import config


# ===================
#  Helper functions
# ===================


def random_suffix():
    """Helper function to generate a random suffix"""
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    """Helper function to generate a random sku"""
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    """Helper function to generate a random backref"""
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    """Helper function to generate a random orderid"""
    return f"order-{name}-{random_suffix()}"


# ===================
#  End to end tests
# ===================


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock(
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "quantity": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "quantity": 20}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
