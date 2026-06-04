from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    label: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

class DeviceTypeBase(BaseModel):
    label: str
    category_id: int

class DeviceTypeCreate(DeviceTypeBase):
    pass

class DeviceTypeUpdate(BaseModel):
    label: str

class DeviceTypeOut(DeviceTypeBase):
    id: int

class DeviceConfigBase(BaseModel):
    category_id: int
    device_type_id: int
    station_number: int = 1
    baud_rate: int = 115200
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'none'
    purpose: str = ''

class DeviceConfigCreate(DeviceConfigBase):
    pass

class DeviceConfigUpdate(BaseModel):
    station_number: Optional[int] = None
    baud_rate: Optional[int] = None
    data_bits: Optional[int] = None
    stop_bits: Optional[int] = None
    parity: Optional[str] = None
    purpose: Optional[str] = None

class DeviceConfigOut(DeviceConfigBase):
    id: int
    project_id: int

class ProjectBase(BaseModel):
    name: str
    description: str = ''

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    device_configs: List[DeviceConfigOut] = []

class SerialConnectRequest(BaseModel):
    port_name: str
    baud_rate: int = 115200
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'none'

class ModbusWriteRequest(BaseModel):
    station_number: int
    address: int = 0
    value: int

class ModbusWriteConfigRequest(BaseModel):
    station_number: int
    baud_rate: int
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'none'

class InspectRequest(BaseModel):
    station_number: int

class InspectResult(BaseModel):
    name: str
    passed: bool
    detail: str = ''
