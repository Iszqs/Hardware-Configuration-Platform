from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category, DeviceType, Project, DeviceConfig
from datetime import datetime

router = APIRouter(prefix='/api/migrate', tags=['数据迁移'])

@router.get('/has-data')
def has_data(db: Session = Depends(get_db)):
    count = db.query(Category).count()
    return {'has_data': count > 0}

@router.post('/import')
def import_data(data: dict, db: Session = Depends(get_db)):
    cat_map = {}
    type_map = {}

    for cat in data.get('categories', []):
        label = cat.get('label', '')
        existing = db.query(Category).filter(Category.id == cat.get('id')).first()
        if existing:
            cat_map[cat['id']] = existing.id
            continue
        db_cat = Category(label=label)
        db.add(db_cat)
        db.flush()
        cat_map[cat['id']] = db_cat.id

    for dt in data.get('allDeviceTypes', []):
        db_dt = DeviceType(
            label=dt['label'],
            category_id=cat_map.get(dt.get('categoryId', ''), 1)
        )
        db.add(db_dt)
        db.flush()
        type_map[dt['id']] = db_dt.id

    for proj in data.get('projects', []):
        db_proj = Project(
            name=proj.get('name', ''),
            description=proj.get('description', ''),
        )
        if 'createdAt' in proj:
            try:
                db_proj.created_at = datetime.fromisoformat(proj['createdAt'])
            except ValueError:
                pass
        db.add(db_proj)
        db.flush()

        for cfg in proj.get('deviceConfigs', []):
            db_cfg = DeviceConfig(
                project_id=db_proj.id,
                category_id=cat_map.get(cfg.get('categoryId', ''), 1),
                device_type_id=type_map.get(cfg.get('deviceTypeId', ''), 1),
                station_number=cfg.get('stationNumber', 1),
                baud_rate=cfg.get('baudRate', 9600),
                data_bits=cfg.get('dataBits', 8),
                stop_bits=cfg.get('stopBits', 1),
                parity=cfg.get('parity', 'none'),
                purpose=cfg.get('purpose', '')
            )
            db.add(db_cfg)

    db.commit()
    return {
        'status': 'ok',
        'message': f'迁移完成: {len(cat_map)} 分类, {len(type_map)} 设备类型, {len(data.get("projects", []))} 项目'
    }
