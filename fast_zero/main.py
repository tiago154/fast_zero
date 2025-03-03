from fastapi import FastAPI

from fast_zero.app_v1.routes import router as v1_router
from fast_zero.app_v2.routes import router as v2_router

app = FastAPI()

app.include_router(v1_router, prefix='/api/v1', tags=['v1'])
app.include_router(v2_router, prefix='/api/v2', tags=['v2'])
