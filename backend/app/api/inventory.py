from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.services.inventory import InventoryService
from app.models.models import Material, StockMovement

router = APIRouter(prefix="/inventory", tags=["inventory"])


class MaterialCreate(BaseModel):
    code: str
    name_ar: str
    name_en: str
    unit: str
    unit_cost: Decimal
    reorder_level: Decimal = Decimal("0")
    category_id: int
    supplier: Optional[str] = None


class MovementCreate(BaseModel):
    material_id: int
    movement_type: str          # in | out
    qty: Decimal                # الوزن / الكمية دائماً بالوحدة الأساسية
    unit_cost: Decimal
    reference: Optional[str] = None
    notes: Optional[str] = None
    movement_date: date
    # حقول السحب الجديدة
    withdrawal_unit: Optional[str] = None     # weight | piece
    withdrawal_type: Optional[str] = None     # legacy alias
    destination: Optional[str] = None         # workshop | customer
    destination_ref: Optional[str] = None
    pieces_count: Optional[int] = None
    weight_per_piece: Optional[Decimal] = None
    weight_per_piece: Optional[Decimal] = None  # وزن القطعة بالكيلو


@router.post("/materials", status_code=201)
async def create_material(data: MaterialCreate, db: AsyncSession = Depends(get_db)):
    return await InventoryService.create_material(db, data)


@router.get("/materials")
async def list_materials(low_stock_only: bool = False, db: AsyncSession = Depends(get_db)):
    return await InventoryService.list_materials(db, low_stock_only)


@router.get("/materials/{material_id}")
async def get_material(material_id: int, db: AsyncSession = Depends(get_db)):
    mat = await InventoryService.get_material(db, material_id)
    if not mat: raise HTTPException(404, "Material not found")
    return mat


@router.put("/materials/{material_id}")
async def update_material(material_id: int, data: MaterialCreate, db: AsyncSession = Depends(get_db)):
    mat = await db.get(Material, material_id)
    if not mat: raise HTTPException(404)
    for k, v in data.model_dump().items():
        setattr(mat, k, v)
    await db.commit()
    await db.refresh(mat)
    return {"id": mat.id, "code": mat.code, "name_ar": mat.name_ar,
            "unit_cost": float(mat.unit_cost), "stock_qty": float(mat.stock_qty)}


@router.post("/movements", status_code=201)
async def record_movement(data: MovementCreate, db: AsyncSession = Depends(get_db)):
    # لو السحب بالقطع - احسب الوزن الإجمالي
    actual_qty = data.qty
    withdrawal_unit = getattr(data, 'withdrawal_unit', None) or getattr(data, 'withdrawal_type', None)
    pieces_count = getattr(data, 'pieces_count', None)
    weight_per_piece = getattr(data, 'weight_per_piece', None)

    if withdrawal_unit == "piece" and pieces_count and weight_per_piece:
        actual_qty = Decimal(str(pieces_count)) * Decimal(str(weight_per_piece))

    total = actual_qty * data.unit_cost
    movement = StockMovement(
        material_id=data.material_id,
        movement_type=data.movement_type,
        qty=actual_qty,
        unit_cost=data.unit_cost,
        total_cost=total,
        reference=data.reference,
        notes=getattr(data, 'notes', None),
        movement_date=data.movement_date,
        withdrawal_unit=withdrawal_unit,
        destination=getattr(data, 'destination', None),
        destination_ref=getattr(data, 'destination_ref', None),
        pieces_count=pieces_count,
        weight_per_piece=Decimal(str(weight_per_piece)) if weight_per_piece else None,
    )
    db.add(movement)

    mat = await db.get(Material, data.material_id)
    if mat:
        if data.movement_type == "in":
            mat.stock_qty += actual_qty
            mat.unit_cost = data.unit_cost
        else:
            mat.stock_qty -= actual_qty

    await db.commit()
    await db.refresh(movement)
    return {
        "id": movement.id,
        "actual_qty": float(actual_qty),
        "total_cost": float(total),
        "pieces_count": movement.pieces_count,
        "destination": movement.destination,
    }


@router.get("/movements/{material_id}")
async def get_movements(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StockMovement)
        .where(StockMovement.material_id == material_id)
        .order_by(StockMovement.movement_date.desc())
    )
    movs = result.scalars().all()
    dest_ar = {"workshop": "الورشة", "customer": "عميل خارجي"}
    return [{
        "id": m.id, "movement_type": m.movement_type,
        "qty": float(m.qty), "unit_cost": float(m.unit_cost),
        "total_cost": float(m.total_cost),
        "movement_date": str(m.movement_date),
        "reference": m.reference, "notes": m.notes,
        "withdrawal_unit": getattr(m, "withdrawal_unit", None),
        "destination": m.destination,
        "destination_ar": dest_ar.get(m.destination or "", m.destination or ""),
        "destination_ref": m.destination_ref,
        "pieces_count": m.pieces_count,
        "weight_per_piece": float(m.weight_per_piece) if m.weight_per_piece else None,
    } for m in movs]


@router.get("/alerts/low-stock")
async def low_stock_alerts(db: AsyncSession = Depends(get_db)):
    items = await InventoryService.low_stock_alerts(db)
    return [{"id": m.id, "code": m.code, "name_ar": m.name_ar,
             "stock_qty": float(m.stock_qty), "reorder_level": float(m.reorder_level)} for m in items]


@router.put("/materials/{material_id}/price")
async def update_material_price(material_id: int, new_price: float,
                                 db: AsyncSession = Depends(get_db)):
    """تحديث سعر المادة — يُحدِّث BOM تلقائياً عبر الـ trigger"""
    mat = await db.get(Material, mat_id := material_id)
    if not mat: raise HTTPException(404, "Material not found")
    mat.unit_cost = new_price
    await db.commit()
    return {"id": mat.id, "code": mat.code, "new_price": float(mat.unit_cost)}
