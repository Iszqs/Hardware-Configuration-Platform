from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import DeviceType

router = APIRouter(prefix='/api/device-types', tags=['硬件类型'])

@router.get('')
def list_device_types(db: Session = Depends(get_db)):
    return db.query(DeviceType).order_by(DeviceType.id).all()

@router.get('/by-category/{category_id}')
def list_by_category(category_id: int, db: Session = Depends(get_db)):
    return db.query(DeviceType).filter(DeviceType.category_id == category_id).order_by(DeviceType.id).all()

@router.post('', status_code=201)
def create_device_type(data: dict, db: Session = Depends(get_db)):
    dt = DeviceType(label=data['label'], category_id=data['category_id'])
    db.add(dt)
    db.commit()
    db.refresh(dt)
    return dt

@router.put('/{type_id}')
def update_device_type(type_id: int, data: dict, db: Session = Depends(get_db)):
    dt = db.query(DeviceType).filter(DeviceType.id == type_id).first()
    if not dt:
        raise HTTPException(404, '硬件类型不存在')
    dt.label = data['label']
    db.commit()
    db.refresh(dt)
    return dt

@router.delete('/{type_id}', status_code=204)
def delete_device_type(type_id: int, db: Session = Depends(get_db)):
    dt = db.query(DeviceType).filter(DeviceType.id == type_id).first()
    if not dt:
        raise HTTPException(404, '硬件类型不存在')
    db.delete(dt)
    db.commit()
