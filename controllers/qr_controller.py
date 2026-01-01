import uuid
import segno
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.restaurant_table import RestaurantTable
from models.qr_code import QRCode
from schemas.table_schema import TableCreate, TableOut

router = APIRouter(prefix="/tables", tags=["Tables"])
@router.post("", response_model=TableOut)
def create_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
):
    # 1. Tạo bàn
    table = RestaurantTable(
        restaurant_id=payload.restaurant_id,
        name=payload.name,
        seats=payload.seats,
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    # 2. Tạo QR record
    qr = QRCode(
        restaurant_id=table.restaurant_id,
        table_id=table.id,
        code=str(uuid.uuid4()),
        type="table",
        status="active",
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)

    # 3. TẠO FILE QR IMAGE
    qr_dir = Path("media/qrs")
    qr_dir.mkdir(parents=True, exist_ok=True)

    qr_url = f"http://localhost:8000/guest/scan?code={qr.code}"

    qr_img = segno.make(qr_url)

    file_name = f"table-{table.id}.png"
    file_path = qr_dir / file_name

    qr_img.save(
        file_path,
        scale=10,
        border=4
    )

    # 4. LƯU PATH VÀO DB
    qr.image_path = f"/media/qrs/{file_name}"
    db.commit()

    return table
