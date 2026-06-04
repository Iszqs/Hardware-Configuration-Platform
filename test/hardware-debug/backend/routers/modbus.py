from fastapi import APIRouter, HTTPException
from backend.services import modbus_service
import asyncio

router = APIRouter(prefix='/api/modbus', tags=['Modbus通信'])


@router.post('/write-config-57')
async def write_config_57(data: dict):
    """57电机配置：写入波特率"""
    station = data.get('station_number', 1)
    baud_rate = data.get('baud_rate', 115200)
    return await asyncio.to_thread(modbus_service.write_config_57, station, baud_rate)


@router.post('/inspect-57')
async def inspect_57(data: dict):
    """57电机检测：验证站号和波特率"""
    station = data.get('station_number', 1)
    baud_rate = data.get('baud_rate', 115200)
    return await asyncio.to_thread(modbus_service.inspect_57, station, baud_rate)


@router.post('/write-config-35')
async def write_config_35(data: dict):
    """35电机配置：写入站号和波特率"""
    current_station = data.get('current_station', 1)
    target_station = data.get('target_station', 1)
    target_baud_rate = data.get('target_baud_rate', 115200)
    return await asyncio.to_thread(modbus_service.write_config_35, current_station, target_station, target_baud_rate)


@router.post('/inspect-35')
async def inspect_35(data: dict):
    """35电机检测：验证站号和波特率"""
    station = data.get('station_number', 1)
    target_station = data.get('target_station', 1)
    target_baud_rate = data.get('target_baud_rate', 115200)
    return await asyncio.to_thread(modbus_service.inspect_35, station, target_station, target_baud_rate)
