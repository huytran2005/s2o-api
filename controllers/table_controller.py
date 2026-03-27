import os
from pathlib import Path
from typing import Annotated, List
import uuid
from uuid import UUID

import segno
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.guest_session import GuestSession
from models.qr_code import QRCode
from models.restaurant_table import RestaurantTable
from schemas.table_schema import TableCreate, TableOut, TableUpdate
from utils.dependencies import get_current_user

router = APIRouter(prefix="/tables", tags=["Tables"])

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

QR_DIR = Path("media/qrs")
TABLE_NOT_FOUND_DETAIL = "Table not found"


@router.post("", response_model=TableOut)
def create_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
):
    existed = db.query(RestaurantTable).filter(
        RestaurantTable.restaurant_id == payload.restaurant_id,
        RestaurantTable.name == payload.name
    ).first()

    if existed:
        raise HTTPException(
            status_code=400,
            detail="Tên bàn đã tồn tại"
        )
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
    table_id: UUID,
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
            detail=TABLE_NOT_FOUND_DETAIL
        )

    return table

@router.put("/{table_id}", response_model=TableOut)
def update_table(
    table_id: UUID,
    payload: TableUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    table = db.query(RestaurantTable).filter(
        RestaurantTable.id == table_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail=TABLE_NOT_FOUND_DETAIL)

    # ===== CHECK TRÙNG TÊN =====
    if payload.name and payload.name != table.name:
        existed = db.query(RestaurantTable).filter(
            RestaurantTable.restaurant_id == table.restaurant_id,
            RestaurantTable.name == payload.name,
            RestaurantTable.id != table.id,   # 🔥 QUAN TRỌNG
        ).first()

        if existed:
            raise HTTPException(
                status_code=400,
                detail="Table name already exists"
            )

        table.name = payload.name

    # ===== UPDATE SEATS =====
    if payload.seats is not None:
        table.seats = payload.seats

    db.commit()
    db.refresh(table)
    return table

def delete_qr_image(table_id: UUID):
    qr_path = Path("media/qrs") / f"table-{table_id}.png"
    if qr_path.exists():
        qr_path.unlink()


@router.delete("/{table_id}", status_code=204)
def delete_table(
    table_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. check table
    table = db.query(RestaurantTable).filter_by(id=table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail=TABLE_NOT_FOUND_DETAIL)

    # 2. lấy danh sách qr_code id của table này
    qr_ids = (
        db.query(QRCode.id)
        .filter(QRCode.table_id == table_id)
        .subquery()
    )

    # 3. delete guest_session (🔥 QUAN TRỌNG)
    db.query(GuestSession).filter(
        GuestSession.qr_id.in_(qr_ids)
    ).delete(synchronize_session=False)

    # 4. delete qr_code
    db.query(QRCode).filter(QRCode.table_id == table_id).delete()

    # 5. delete qr image
    delete_qr_image(table_id)

    # 6. delete table
    db.delete(table)
    db.commit()
@router.get("", response_model=List[TableOut])
def get_all_tables(
    db: Session = Depends(get_db),
):
    tables = db.query(RestaurantTable).all()
    return tables
