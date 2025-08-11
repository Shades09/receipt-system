from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Receipt, Item
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import io, os
from fastapi.responses import StreamingResponse

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

    # A5 size at 150 DPI: 1748 x 2480 pixels (portrait)
    width, height = 1748, 2480
    img = Image.new("RGB", (width, height), color="white")
    d = ImageDraw.Draw(img)

    # Load Poppins font (fallback to default if missing)
    try:
        font_path = os.path.join(os.path.dirname(__file__), "Poppins-Regular.ttf")
        font_bold = ImageFont.truetype(font_path, 60)
        font = ImageFont.truetype(font_path, 36)
        font_small = ImageFont.truetype(font_path, 28)
    except Exception:
        font_bold = font = font_small = ImageFont.load_default()

    # Logo placeholder (replace with your logo if available)
    d.rectangle([80, 80, 280, 280], fill="#e0e0e0", outline="#888")
    d.text((100, 180), "LOGO", font=font_small, fill="#888")

    # Heading
    d.text((340, 120), "CONSULT JULES", font=font_bold, fill="#7c3aed")
    d.text((340, 200), "SERVICES", font=font, fill="#7c3aed")

    # Add a light border around the receipt
    d.rectangle([60, 60, width-60, height-60], outline="#a78bfa", width=6)

    # Add a horizontal line under the header
    d.line([(80, 300), (width-80, 300)], fill="#a78bfa", width=3)

    # Billed To
    d.text((80, 340), "Billed To:", font=font, fill="#222")
    d.text((250, 340), f"{receipt.customer}", font=font, fill="#222")

    # Receipt No, Issued Date, PO No
    d.text((80, 420), f"Receipt No: CJ-{receipt.id:05d}", font=font_small, fill="#222")
    issued_date = ""
    if hasattr(receipt, "created_at") and receipt.created_at:
        issued_date = receipt.created_at.strftime('%Y-%m-%d')
    d.text((80, 470), f"Issued Date: {issued_date}", font=font_small, fill="#222")
    d.text((80, 520), f"Purchase Order No: Cj00{receipt.id:05d}", font=font_small, fill="#222")

    # Summary
    d.text((80, 600), "Summary:", font=font, fill="#222")
    d.text((250, 600), f"Payment made for TUITION", font=font, fill="#222")

    # Use a light gray box for the summary
    d.rectangle([80, 600, width-80, 670], fill="#f3f4f6")
    d.text((100, 620), "Summary: Payment made for TUITION", font=font, fill="#222")

    # Table headings
    table_y = 700
    d.rectangle([80, table_y, width-80, table_y+60], fill="#ede9fe")
    d.text((100, table_y+10), "Item", font=font_small, fill="#4F46E5")
    d.text((400, table_y+10), "Description", font=font_small, fill="#4F46E5")
    d.text((900, table_y+10), "Quantity", font=font_small, fill="#4F46E5")
    d.text((1150, table_y+10), "Unit Price", font=font_small, fill="#4F46E5")
    d.text((1400, table_y+10), "Amount", font=font_small, fill="#4F46E5")

    # Table rows
    y = table_y + 70
    for idx, item in enumerate(receipt.items):
        d.text((100, y), str(idx+1), font=font_small, fill="#222")
        d.text((400, y), item.name, font=font_small, fill="#222")  # Using name as description
        d.text((900, y), str(item.qty), font=font_small, fill="#222")
        d.text((1150, y), f"{item.price:.2f}", font=font_small, fill="#222")
        d.text((1400, y), f"{item.qty * item.price:.2f}", font=font_small, fill="#222")
        y += 50

    # Subtotal, Total
    y += 40
    subtotal = sum(item.qty * item.price for item in receipt.items)
    d.text((1150, y), "SUB TOTAL", font=font_small, fill="#222")
    d.text((1400, y), f"{subtotal:.2f}", font=font_small, fill="#222")
    y += 40
    d.text((1150, y), "TOTAL", font=font_small, fill="#4F46E5")
    d.text((1400, y), f"{receipt.total:.2f}", font=font_small, fill="#4F46E5")

    # Add a horizontal line above totals
    d.line([(80, y+20), (width-80, y+20)], fill="#a78bfa", width=2)

    # Save to buffer
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
