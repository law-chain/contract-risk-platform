from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.goods_service import GoodsService
from app.schemas.goods_service import GoodsServiceCreate, GoodsServiceUpdate, GoodsServiceResponse

router = APIRouter(prefix="/api/engagements/{engagement_id}/goods-services", tags=["goods_services"])


@router.get("/", response_model=List[GoodsServiceResponse])
def list_goods_services(engagement_id: int, db: Session = Depends(get_db)):
    return db.query(GoodsService).filter(GoodsService.engagement_id == engagement_id).all()


@router.post("/", response_model=GoodsServiceResponse, status_code=201)
def create_goods_service(engagement_id: int, data: GoodsServiceCreate, db: Session = Depends(get_db)):
    gs = GoodsService(engagement_id=engagement_id, **data.model_dump())
    db.add(gs)
    db.commit()
    db.refresh(gs)
    return gs


@router.get("/{gs_id}", response_model=GoodsServiceResponse)
def get_goods_service(engagement_id: int, gs_id: int, db: Session = Depends(get_db)):
    gs = db.query(GoodsService).filter(GoodsService.id == gs_id, GoodsService.engagement_id == engagement_id).first()
    if not gs:
        raise HTTPException(status_code=404, detail="Goods/Service not found")
    return gs


@router.put("/{gs_id}", response_model=GoodsServiceResponse)
def update_goods_service(engagement_id: int, gs_id: int, data: GoodsServiceUpdate, db: Session = Depends(get_db)):
    gs = db.query(GoodsService).filter(GoodsService.id == gs_id, GoodsService.engagement_id == engagement_id).first()
    if not gs:
        raise HTTPException(status_code=404, detail="Goods/Service not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(gs, key, value)
    db.commit()
    db.refresh(gs)
    return gs


@router.delete("/{gs_id}", status_code=204)
def delete_goods_service(engagement_id: int, gs_id: int, db: Session = Depends(get_db)):
    gs = db.query(GoodsService).filter(GoodsService.id == gs_id, GoodsService.engagement_id == engagement_id).first()
    if not gs:
        raise HTTPException(status_code=404, detail="Goods/Service not found")
    db.delete(gs)
    db.commit()
