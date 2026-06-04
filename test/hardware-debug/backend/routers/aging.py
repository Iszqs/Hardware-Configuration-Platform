from fastapi import APIRouter, HTTPException
import asyncio
from typing import Optional

from backend.services import modbus_service
from backend.services.log_service import add_log

router = APIRouter(prefix='/api/aging', tags=['老化测试'])

# ── 全局老化测试状态 ──
_aging_state = {
    'running': False,
    'current_point': 0,
    'total_points': 0,
    'current_position': None,
    'points': [],
    'dwell_ms': 1000,
    'cycle_count': 0,
    'max_cycles': 0,  # 0 = unlimited
    'elapsed_seconds': 0,
    'speed_rpm': 300,
    'accel_ms': 120,
    'decel_ms': 120,
    'station': 1,
    'logs': [],
    'start_time': None,
}

_aging_task: Optional[asyncio.Task] = None


def _add_aging_log(message: str, type: str = 'info'):
    import time
    ts = time.strftime('%H:%M:%S')
    _aging_state['logs'].append(f'[{ts}] {message}')
    if len(_aging_state['logs']) > 500:
        _aging_state['logs'] = _aging_state['logs'][-500:]
    add_log(f'[老化测试] {message}', type)


async def _aging_loop():
    """后台老化测试主循环"""
    state = _aging_state
    import time

    station = state['station']
    points = state['points']
    dwell_s = state['dwell_ms'] / 1000.0
    max_cycles = state['max_cycles']

    _add_aging_log('老化测试开始', 'success')

    # 1. 确保串口连接
    if not modbus_service.ensure_connected():
        _add_aging_log('串口未连接，无法开始老化测试', 'error')
        state['running'] = False
        return

    # 2. 设置速度、加减速
    modbus_service.set_speed(station, state['speed_rpm'])
    await asyncio.sleep(0.1)
    modbus_service.set_accel_decel(station, state['accel_ms'], state['decel_ms'])

    # 3. 使能电机
    modbus_service.motor_enable(station, True)
    await asyncio.sleep(0.2)

    state['cycle_count'] = 0
    state['start_time'] = time.time()
    total_points = len(points)
    state['total_points'] = total_points

    if total_points == 0:
        _add_aging_log('坐标点列表为空，无法执行', 'error')
        state['running'] = False
        return

    try:
        while state['running']:
            for idx, pt in enumerate(points):
                if not state['running']:
                    break

                position = pt['position']
                dwell = pt.get('dwell', state['dwell_ms']) / 1000.0

                state['current_point'] = idx + 1
                _add_aging_log(f'移动到点位 #{idx + 1}, 位置={position}')

                # 发送绝对位置移动命令
                modbus_service.move_to_absolute(station, position)
                state['current_position'] = position

                # 等待到位（超时保护 30 秒）
                waited = 0
                max_wait = 30.0
                while state['running'] and waited < max_wait:
                    if modbus_service.is_in_position(station):
                        _add_aging_log(f'点位 #{idx + 1} 到位, 位置={position}', 'success')
                        break
                    await asyncio.sleep(0.1)
                    waited += 0.1

                if waited >= max_wait:
                    _add_aging_log(f'点位 #{idx + 1} 到位超时', 'warning')

                # 停留
                if state['running'] and dwell > 0:
                    await asyncio.sleep(dwell)

                # 更新运行时间
                state['elapsed_seconds'] = int(time.time() - state['start_time'])

            # 完成一轮
            if state['running']:
                state['cycle_count'] += 1
                state['elapsed_seconds'] = int(time.time() - state['start_time'])
                _add_aging_log(f'第 {state["cycle_count"]} 轮完成', 'success')

                if max_cycles > 0 and state['cycle_count'] >= max_cycles:
                    _add_aging_log(f'达到最大循环次数 {max_cycles}，停止老化测试', 'info')
                    state['running'] = False
                    break

    except Exception as e:
        _add_aging_log(f'老化测试异常: {e}', 'error')
    finally:
        state['running'] = False
        _add_aging_log('老化测试结束', 'info')


@router.post('/start')
async def aging_start(data: dict):
    """开始老化测试"""
    global _aging_task

    if _aging_state['running']:
        raise HTTPException(400, '老化测试已在运行中')

    # 解析参数
    points = data.get('points', [])
    if not points or len(points) == 0:
        raise HTTPException(400, '坐标点列表不能为空')

    _aging_state['points'] = points
    _aging_state['dwell_ms'] = data.get('dwell_ms', 1000)
    _aging_state['max_cycles'] = data.get('max_cycles', 0)  # 0=无限
    _aging_state['speed_rpm'] = data.get('speed_rpm', 300)
    _aging_state['accel_ms'] = data.get('accel_ms', 120)
    _aging_state['decel_ms'] = data.get('decel_ms', 120)
    _aging_state['station'] = data.get('station', 1)
    _aging_state['current_point'] = 0
    _aging_state['cycle_count'] = 0
    _aging_state['elapsed_seconds'] = 0
    _aging_state['logs'] = []
    _aging_state['start_time'] = None
    _aging_state['running'] = True
    _aging_state['total_points'] = len(points)

    # 启动后台任务
    _aging_task = asyncio.create_task(_aging_loop())

    max_cycles_val = _aging_state["max_cycles"]
    cycle_text = "无限循环" if max_cycles_val == 0 else f"{max_cycles_val} 次"
    return {
        'success': True,
        'message': f'老化测试已启动, {len(points)} 个坐标点, {cycle_text}'
    }


@router.post('/stop')
async def aging_stop():
    """停止老化测试"""
    if not _aging_state['running']:
        raise HTTPException(400, '老化测试未在运行')
    _aging_state['running'] = False
    return {'success': True, 'message': '老化测试已停止'}


@router.get('/status')
async def aging_status():
    """获取老化测试状态"""
    s = _aging_state
    return {
        'running': s['running'],
        'current_point': s['current_point'],
        'total_points': s['total_points'],
        'current_position': s['current_position'],
        'cycle_count': s['cycle_count'],
        'max_cycles': s['max_cycles'],
        'elapsed_seconds': s['elapsed_seconds'],
        'speed_rpm': s['speed_rpm'],
        'dwell_ms': s['dwell_ms'],
        'station': s['station'],
        'logs': s['logs'][-50:],  # 最近50条
    }


@router.post('/move-to')
async def aging_move_to(data: dict):
    """手动移动到指定绝对位置"""
    position = data.get('position')
    station = data.get('station', 1)
    if position is None:
        raise HTTPException(400, '缺少 position')
    if not modbus_service.ensure_connected():
        raise HTTPException(500, '串口未连接')

    # 可选: 设置速度
    speed = data.get('speed_rpm')
    if speed:
        modbus_service.set_speed(station, speed)

    modbus_service.motor_enable(station, True)
    ok = modbus_service.move_to_absolute(station, position)
    if ok:
        return {'success': True, 'message': f'正在移动到 {position}'}
    else:
        raise HTTPException(500, '移动命令发送失败')


@router.post('/home')
async def aging_home(data: dict):
    """回原点"""
    station = data.get('station', 1)
    direction = data.get('direction', 0)
    speed = data.get('speed_rpm', 200)

    if not modbus_service.ensure_connected():
        raise HTTPException(500, '串口未连接')

    modbus_service.motor_enable(station, True)
    ok = modbus_service.home_return(station, direction, speed)
    if ok:
        return {'success': True, 'message': f'正在回原点'}
    else:
        raise HTTPException(500, '回原点命令发送失败')


@router.post('/stop-motor')
async def aging_stop_motor(data: dict):
    """急停电机"""
    station = data.get('station', 1)
    emergency = data.get('emergency', False)

    if not modbus_service.ensure_connected():
        raise HTTPException(500, '串口未连接')

    if emergency:
        ok = modbus_service.emergency_stop(station)
    else:
        ok = modbus_service.stop_decelerate(station)
    return {'success': ok, 'message': '急停' if emergency else '减速停止'}


@router.post('/enable')
async def aging_enable(data: dict):
    """使能/脱机"""
    station = data.get('station', 1)
    enable = data.get('enable', True)
    if not modbus_service.ensure_connected():
        raise HTTPException(500, '串口未连接')
    ok = modbus_service.motor_enable(station, enable)
    return {'success': ok, 'message': '使能' if enable else '脱机'}


@router.get('/position')
async def aging_position(station: int = 1):
    """读取当前位置"""
    pos = modbus_service.read_position(station)
    if pos is not None:
        return {'position': pos, 'station': station}
    return {'position': None, 'station': station, 'error': '读取失败'}
