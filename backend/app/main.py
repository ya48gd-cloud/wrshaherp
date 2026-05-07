from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.inventory import router as inventory_router
from app.api.equipment import router as equipment_router
from app.api.accounting import router as accounting_router
from app.api.cad import router as cad_router
from app.api.workers import router as workers_router
from app.api.auth import router as auth_router
from app.api.sales import router as sales_router
from app.api.customers import router as customers_router
from app.api.attendance import router as attendance_router

app = FastAPI(
    title="Heavy Equipment Workshop ERP",
    description="نظام ERP لورشة تصنيع المعدات الثقيلة",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory_router,  prefix="/api/v1")
app.include_router(equipment_router,  prefix="/api/v1")
app.include_router(accounting_router, prefix="/api/v1")
app.include_router(cad_router,        prefix="/api/v1")
app.include_router(workers_router,    prefix="/api/v1")
app.include_router(auth_router,       prefix="/api/v1")
app.include_router(sales_router,      prefix="/api/v1")
app.include_router(customers_router,  prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Heavy ERP API running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
