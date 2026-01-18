import uuid
import os
import segno
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.restaurant_table import RestaurantTable
from models.qr_code import QRCode
from schemas.table_schema import TableCreate, TableOut

router = APIRouter(prefix="/tables", tags=["Tables"])

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise RuntimeError("BASE_URL must be set")

QR_DIR = Path("media/qrs")


@router.post("", response_model=TableOut)
def create_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
):
    # 1. Create table
    table = RestaurantTable(
        restaurant_id=payload.restaurant_id,
        name=payload.name,
        seats=payload.seats,
        status="active",
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    # 2. Create QR record
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

    # 3. Generate QR image (POINT TO BACKEND)
    QR_DIR.mkdir(parents=True, exist_ok=True)

    qr_url = f"{BASE_URL}/qr-entry?code={qr.code}"

    qr_img = segno.make(qr_url)

    file_name = f"table-{table.id}.png"
    file_path = QR_DIR / file_name

    qr_img.save(
        file_path,
        scale=10,
        border=4,
    )

    # 4. Save image path
    qr.image_path = f"/media/qrs/{file_name}"
    db.commit()

    return table

@router.get("/{table_id}", response_model=TableOut)
def get_table_by_id(
    table_id: int,
    db: Session = Depends(get_db),
):
    table = (
        db.query(RestaurantTable)
        .filter(RestaurantTable.id == table_id)
        .first()
    )

    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    return table
from typing import List

@router.get("", response_model=List[TableOut])
def get_all_tables(
    db: Session = Depends(get_db),
):
    tables = db.query(RestaurantTable).all()
    return tables