from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category

router = APIRouter(prefix='/api/categories', tags=['分类'])

@router.get('')
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id).all()

@router.post('', status_code=201)
def create_category(data: dict, db: Session = Depends(get_db)):
    cat = Category(label=data['label'])
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.put('/{category_id}')
def update_category(category_id: int, data: dict, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(404, '分类不存在')
    cat.label = data['label']
    db.commit()
    db.refresh(cat)
    return cat

@router.delete('/{category_id}', status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(404, '分类不存在')
    db.delete(cat)
    db.commit()
