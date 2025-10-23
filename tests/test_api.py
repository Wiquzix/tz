import pytest
import httpx
import time
from uuid import UUID

BASE_URL = "http://127.0.0.1:8000/api/v1"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def _create_customer(client, name: str) -> str:
    r = client.post("/customers/", json={"full_name": name})
    r.raise_for_status()
    return r.json()["uuid"]


def _delete_customer(client, uid: str) -> None:
    client.delete(f"/customers/{uid}")


def test_get_customers_list(client):
    r = client.get("/customers/")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data["items"], list)
    assert "total" in data


def test_get_single_customer(client):
    # try to get a customer; if none exist create one and cleanup afterwards
    r = client.get("/customers/")
    assert r.status_code == 200
    items = r.json()["items"]
    created = None
    try:
        if not items:
            # create temporary customer
            name = f"pytest-customer-{int(time.time()*1000)}"
            created = _create_customer(client, name)
            cust_id = created
        else:
            cust_id = items[0]["uuid"]

        r2 = client.get(f"/customers/{cust_id}")
        assert r2.status_code == 200
        cdata = r2.json()
        assert cdata["uuid"] == cust_id
        assert "full_name" in cdata
    finally:
        if created:
            _delete_customer(client, created)


def test_create_update_delete_vegetable(client):
    # create
    payload = {"title": "pytest-veggie", "weight": 10, "price": 5, "length": 2}
    r = client.post("/vegetables/", json=payload)
    assert r.status_code == 200
    veg = r.json()
    vid = veg["uuid"]
    assert UUID(vid)

    # update
    payload_update = {"title": "pytest-veggie-upd", "weight": 12, "price": 6, "length": 3}
    r2 = client.put(f"/vegetables/{vid}", json=payload_update)
    assert r2.status_code == 200
    updated = r2.json()
    assert updated["title"] == payload_update["title"]

    # delete
    r3 = client.delete(f"/vegetables/{vid}")
    assert r3.status_code == 200
    j = r3.json()
    assert "message" in j
    # ensure it's gone
    rg = client.get(f"/vegetables/{vid}")
    assert rg.status_code == 404


def test_order_lifecycle(client):
    # create a customer for the lifecycle and ensure cleanup
    cust_name = f"pytest-cust-{int(time.time()*1000)}"
    cust_id = _create_customer(client, cust_name)
    try:
        # create a vegetable to order
        payload = {"title": "pytest-veg2", "weight": 20, "price": 7, "length": 4}
        rveg = client.post("/vegetables/", json=payload)
        assert rveg.status_code == 200
        veg = rveg.json()
        veg_id = veg["uuid"]

        # create order
        order_payload = {"vegetable_id": veg_id, "customer_id": cust_id, "quantity": 1}
        rorder = client.post("/orders/", json=order_payload)
        assert rorder.status_code == 200
        order = rorder.json()
        oid = order["uuid"]

        # update order
        upd = {"vegetable_id": veg_id, "customer_id": cust_id, "quantity": 2}
        rupd = client.put(f"/orders/{oid}", json=upd)
        assert rupd.status_code == 200
        assert rupd.json()["quantity"] == 2

        # delete order
        rdel = client.delete(f"/orders/{oid}")
        assert rdel.status_code == 200
        # ensure it's gone
        rget = client.get(f"/orders/{oid}")
        assert rget.status_code == 404

    finally:
        # cleanup vegetable and customer (ignore already-deleted resources)
        client.delete(f"/vegetables/{veg_id}")
        try:
            _delete_customer(client, cust_id)
        except Exception:
            pass
