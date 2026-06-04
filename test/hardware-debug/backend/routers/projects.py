from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Project, DeviceConfig

router = APIRouter(prefix='/api/projects', tags=['项目'])

@router.get('')
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).options(joinedload(Project.device_configs)).order_by(Project.created_at.asc()).all()

@router.post('', status_code=201)
def create_project(data: dict, db: Session = Depends(get_db)):
    project = Project(name=data['name'], description=data.get('description', ''))
    db.add(project)
    db.commit()
    db.refresh(project)
    project.device_configs = []
    return project

@router.get('/{project_id}')
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).options(joinedload(Project.device_configs)).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, '项目不存在')
    return project

@router.put('/{project_id}')
def update_project(project_id: int, data: dict, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, '项目不存在')
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    db.commit()
    db.refresh(project)
    return project

@router.delete('/{project_id}', status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, '项目不存在')
    db.delete(project)
    db.commit()

@router.post('/{project_id}/configs', status_code=201)
def add_device_config(project_id: int, data: dict, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, '项目不存在')
    config = DeviceConfig(
        project_id=project_id,
        category_id=data['category_id'],
        device_type_id=data['device_type_id'],
        station_number=data.get('station_number', 1),
        baud_rate=data.get('baud_rate', 9600),
        data_bits=data.get('data_bits', 8),
        stop_bits=data.get('stop_bits', 1),
        parity=data.get('parity', 'none'),
        custom_name=data.get('custom_name', ''),
        purpose=data.get('purpose', '')
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config

@router.put('/configs/{config_id}')
def update_device_config(config_id: int, data: dict, db: Session = Depends(get_db)):
    config = db.query(DeviceConfig).filter(DeviceConfig.id == config_id).first()
    if not config:
        raise HTTPException(404, '设备配置不存在')
    for key, val in data.items():
        if hasattr(config, key):
            setattr(config, key, val)
    db.commit()
    db.refresh(config)
    return config

@router.delete('/configs/{config_id}', status_code=204)
def delete_device_config(config_id: int, db: Session = Depends(get_db)):
    config = db.query(DeviceConfig).filter(DeviceConfig.id == config_id).first()
    if not config:
        raise HTTPException(404, '设备配置不存在')
    db.delete(config)
    db.commit()
