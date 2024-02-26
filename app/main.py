import logging

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
log = logging.getLogger(__name__)


class Item(BaseModel):
    name: str
    price: float


@app.get("/")
def read_root():
    log.info("info log")
    log.debug("debug log")
    log.error("error log")
    return {"Hello": "World"}


@app.get("/get/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/post")
def post_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}