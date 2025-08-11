from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Receipt, Item
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw
import io

router = APIRouter()

class ItemIn(BaseModel):
    name: str
    qty: int
    price: float

class ReceiptIn(BaseModel):
    customer: str
    items: list[ItemIn]
    tax: float
    discount: float
    payment: str
    total: float

@router.post("/create")
def create_receipt(receipt: ReceiptIn, db: Session = Depends(get_db)):
    db_receipt = Receipt(
        customer=receipt.customer,
        tax=receipt.tax,
        discount=receipt.discount,
        payment=receipt.payment,
        total=receipt.total
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    for item in receipt.items:
        db_item = Item(
            name=item.name,
            qty=item.qty,
            price=item.price,
            receipt_id=db_receipt.id
        )
        db.add(db_item)
    db.commit()
    return {"receipt_id": db_receipt.id}

@router.get("/render/{receipt_id}")
def render_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    img = Image.new("RGB", (600, 400), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), f"Receipt #{receipt.id}\nCustomer: {receipt.customer}", fill=(0,0,0))
    y = 40
    for item in receipt.items:
        d.text((10, y), f"{item.name} x{item.qty} @ {item.price}", fill=(0,0,0))
        y += 20
    d.text((10, y+20), f"Total: ₦{receipt.total}", fill=(0,0,0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")

@router.get("/all")
def list_receipts(db: Session = Depends(get_db)):
    receipts = db.query(Receipt).all()
    return [
        {
            "id": r.id,
            "customer": r.customer,
            "total": r.total,
            "payment": r.payment,
            "tax": r.tax,
            "discount": r.discount
        }
        for r in receipts
    ]
