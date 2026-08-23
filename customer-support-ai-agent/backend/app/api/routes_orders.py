"""GET /orders/{order_id}"""
from fastapi import APIRouter, Depends

from app.api.schemas import OrderStatusResponse
from app.database.session import get_db
from app.tools.order_tools import get_order_status

router = APIRouter(tags=["orders"])


@router.get("/orders/{order_id}", response_model=OrderStatusResponse)
def get_order(order_id: str, db=Depends(get_db)):
    return get_order_status(db, order_id)
