import logging

from fastapi import APIRouter
from pydantic import BaseModel

log = logging.getLogger(__name__)
router = APIRouter()


class Item(BaseModel):
    name: str
    price: float


@router.get("/")
def read_root():
    log.info("info log")
    log.debug("debug log")
    log.error("error log")
    return {"Hello": "World"}


@router.get("/get/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@router.post("/post")
def post_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}
