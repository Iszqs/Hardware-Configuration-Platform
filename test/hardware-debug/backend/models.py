from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(100), nullable=False)

    device_types = relationship('DeviceType', back_populates='category', cascade='all, delete-orphan')

class DeviceType(Base):
    __tablename__ = 'device_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)

    category = relationship('Category', back_populates='device_types')

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), default='')
    created_at = Column(DateTime, server_default=func.now())

    device_configs = relationship('DeviceConfig', back_populates='project', cascade='all, delete-orphan')

class DeviceConfig(Base):
    __tablename__ = 'device_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    device_type_id = Column(Integer, ForeignKey('device_types.id'), nullable=False)
    station_number = Column(Integer, default=1)
    baud_rate = Column(Integer, default=9600)
    data_bits = Column(Integer, default=8)
    stop_bits = Column(Integer, default=1)
    parity = Column(String(20), default='none')
    custom_name = Column(String(200), default='')
    purpose = Column(String(200), default='')

    project = relationship('Project', back_populates='device_configs')
