from fastapi.testclient import TestClient

import app.application as app

client = TestClient(app.APP)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_get():
    response = client.get("/get/1?q=hi")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "q": "hi"}


def test_post():
    response = client.post("/post", json={"name": "Foo", "price": 42.0})
    assert response.status_code == 200
    assert response.json() == {"item_name": "Foo", "item_price": 42.0}
