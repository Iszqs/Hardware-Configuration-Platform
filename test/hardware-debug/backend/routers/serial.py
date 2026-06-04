from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
import serial.tools.list_ports

from backend.services import modbus_service
from backend.services.log_service import save_serial_log, add_log, get_logs, clear_logs

router = APIRouter(prefix='/api/serial', tags=['串口'])

@router.get('/ports')
async def list_ports():
    ports = serial.tools.list_ports.comports()
    return [{'name': p.device, 'description': p.description} for p in ports]

@router.post('/connect')
async def connect(data: dict):
    port_name = data.get('port_name')
    baud_rate = data.get('baud_rate', 115200)
    if not port_name:
        raise HTTPException(400, '缺少串口号')
    add_log(f'正在连接 {port_name} ({baud_rate} bps)...', 'info')
    success = modbus_service.connect(port_name, baud_rate)
    if not success:
        add_log(f'{port_name} 连接失败', 'error')
        raise HTTPException(500, '串口连接失败，请检查端口号和权限')
    add_log(f'{port_name} 连接成功 ({baud_rate} bps)', 'success')
    return {'status': 'connected', 'port': port_name, 'baud_rate': baud_rate}

@router.post('/disconnect')
async def disconnect():
    modbus_service.disconnect()
    add_log('串口已断开', 'info')
    return {'status': 'disconnected'}

@router.get('/status')
async def status():
    return {
        "connected": modbus_service.is_connected(),
        "port": modbus_service.port,
        "baud_rate": modbus_service.baud_rate
    }

@router.get('/logs')
async def get_serial_logs():
    """获取通信日志"""
    return get_logs()

@router.delete('/logs')
async def clear_serial_logs():
    """清空通信日志"""
    clear_logs()
    return {'success': True}

@router.post('/logs')
async def save_log(data: dict):
    message = data.get('message', '')
    log_type = data.get('type', 'info')
    if not message:
        return {'success': False, 'message': '消息不能为空'}
    add_log(message, log_type)
    return {'success': True}

@router.websocket('/ws')
async def serial_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            if modbus_service.is_connected():
                await websocket.send_json({
                    'type': 'status',
                    'connected': True,
                    'message': f'已连接 {modbus_service.port} @ {modbus_service.baud_rate}'
                })
    except WebSocketDisconnect:
        pass
