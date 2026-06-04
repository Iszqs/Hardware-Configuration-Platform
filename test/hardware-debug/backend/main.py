import os
import sys
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import projects, categories, device_types, serial, modbus, migrate, aging

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist')

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title='硬件配置平台 API',
    version='1.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(projects.router)
app.include_router(categories.router)
app.include_router(device_types.router)
app.include_router(serial.router)
app.include_router(modbus.router)
app.include_router(aging.router)
app.include_router(migrate.router)

if os.path.isdir(DIST_DIR):
    app.mount('/assets', StaticFiles(directory=os.path.join(DIST_DIR, 'assets')), name='assets')

    @app.get('/{full_path:path}')
    async def serve_frontend(full_path: str):
        # API 路由不由前端托管
        if full_path.startswith('api/'):
            return {'detail': 'Not Found'}
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(DIST_DIR, 'index.html')
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return {'detail': 'Not Found'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=5175, reload=True)
