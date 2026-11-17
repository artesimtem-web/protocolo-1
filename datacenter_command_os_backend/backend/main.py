import os
from datetime import datetime, date
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    create_engine, String, Integer, Float, Boolean, Date, DateTime, ForeignKey,
    Text, UniqueConstraint, select
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://dc_user:change_me_before_deploy@localhost:5432/datacenter"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Room(TimestampMixin, Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    site: Mapped[str | None] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)

class Rack(TimestampMixin, Base):
    __tablename__ = "racks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"))
    height_u: Mapped[int] = mapped_column(Integer, default=42, nullable=False)
    max_power_w: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)

class Equipment(TimestampMixin, Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    asset_tag: Mapped[str | None] = mapped_column(String(120), unique=True)
    kind: Mapped[str] = mapped_column(String(60), nullable=False, default="server")
    manufacturer: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(120))
    serial_number: Mapped[str | None] = mapped_column(String(160))
    rack_id: Mapped[int | None] = mapped_column(ForeignKey("racks.id", ondelete="SET NULL"))
    start_u: Mapped[int | None] = mapped_column(Integer)
    height_u: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    power_w: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40), default="planned", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

class Interface(TimestampMixin, Base):
    __tablename__ = "interfaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    medium: Mapped[str] = mapped_column(String(60), default="Ethernet cobre", nullable=False)
    mac_address: Mapped[str | None] = mapped_column(String(32))
    ip_address: Mapped[str | None] = mapped_column(String(80))
    vlan: Mapped[str | None] = mapped_column(String(40))
    connected_to: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default="unknown", nullable=False)

class Service(TimestampMixin, Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id", ondelete="SET NULL"))
    endpoint: Mapped[str | None] = mapped_column(String(300))
    criticality: Mapped[str] = mapped_column(String(30), default="Media", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="planned", nullable=False)
    owner: Mapped[str | None] = mapped_column(String(160))

class PowerResource(TimestampMixin, Base):
    __tablename__ = "power_resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(60), nullable=False)
    source: Mapped[str | None] = mapped_column(String(160))
    capacity_w: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    load_w: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    redundancy: Mapped[str] = mapped_column(String(40), default="No definida", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="planned", nullable=False)

class Reservation(TimestampMixin, Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(60), nullable=False)
    resource: Mapped[str] = mapped_column(String(200), nullable=False)
    owner: Mapped[str] = mapped_column(String(160), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Propuesta", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

class Event(TimestampMixin, Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    severity: Mapped[str] = mapped_column(String(30), default="info", nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(160))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

Base.metadata.create_all(engine)

app = FastAPI(
    title="DataCenter Command OS API",
    version="0.1.0",
    description="API inicial para inventario y documentación de infraestructura. No ejecuta cambios en hardware."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

RESOURCES = {
    "rooms": (Room, {"name","site","description"}),
    "racks": (Rack, {"name","room_id","height_u","max_power_w","notes"}),
    "equipment": (Equipment, {"name","asset_tag","kind","manufacturer","model","serial_number","rack_id","start_u","height_u","power_w","status","notes"}),
    "interfaces": (Interface, {"equipment_id","name","medium","mac_address","ip_address","vlan","connected_to","status"}),
    "services": (Service, {"name","description","equipment_id","endpoint","criticality","status","owner"}),
    "power-resources": (PowerResource, {"name","kind","source","capacity_w","load_w","redundancy","status"}),
    "reservations": (Reservation, {"resource_type","resource","owner","start_date","end_date","status","notes"}),
    "events": (Event, {"severity","category","message","source","acknowledged"}),
}
DATE_FIELDS = {"start_date", "end_date"}

class RecordIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data: dict[str, Any]

def serialize(obj):
    result = {}
    for col in obj.__table__.columns:
        value = getattr(obj, col.name)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        result[col.name] = value
    return result

def validate_payload(resource: str, payload: dict, db, exclude_id: int | None = None):
    model, allowed = RESOURCES[resource]
    unknown = set(payload) - allowed
    if unknown:
        raise HTTPException(422, f"Campos no permitidos: {', '.join(sorted(unknown))}")
    for field in ("height_u", "capacity_w", "load_w", "power_w", "max_power_w", "start_u"):
        if field in payload and payload[field] is not None and float(payload[field]) < 0:
            raise HTTPException(422, f"{field} no puede ser negativo")
    if resource == "racks":
        h = int(payload.get("height_u", 42))
        if h < 1 or h > 100:
            raise HTTPException(422, "height_u debe estar entre 1 y 100")
    if resource == "equipment":
        height = int(payload.get("height_u", 1))
        start = payload.get("start_u")
        rack_id = payload.get("rack_id")
        if height < 1:
            raise HTTPException(422, "height_u debe ser al menos 1")
        if start is not None and int(start) < 1:
            raise HTTPException(422, "start_u empieza en U1")
        if rack_id is not None and start is not None:
            rack = db.get(Rack, int(rack_id))
            if not rack:
                raise HTTPException(422, "rack_id no corresponde a un rack existente")
            if int(start) + height - 1 > rack.height_u:
                raise HTTPException(422, f"El equipo excede el rack: U{start} a U{int(start)+height-1}, rack de {rack.height_u}U")
            query = select(Equipment).where(
                Equipment.rack_id == int(rack_id),
                Equipment.start_u.is_not(None)
            )
            if exclude_id is not None:
                query = query.where(Equipment.id != exclude_id)
            for other in db.scalars(query):
                a1, a2 = int(start), int(start) + height - 1
                b1, b2 = other.start_u, other.start_u + other.height_u - 1
                if a1 <= b2 and b1 <= a2:
                    raise HTTPException(409, f"Solapamiento con {other.name} (U{b1}-U{b2})")
    if resource == "reservations":
        start = payload.get("start_date")
        end = payload.get("end_date")
        try:
            start = date.fromisoformat(start) if isinstance(start, str) else start
            end = date.fromisoformat(end) if isinstance(end, str) else end
        except Exception:
            raise HTTPException(422, "Fechas deben usar formato YYYY-MM-DD")
        if start and end and end < start:
            raise HTTPException(422, "end_date no puede ser anterior a start_date")
    if resource == "power-resources":
        capacity = float(payload.get("capacity_w", 0))
        load = float(payload.get("load_w", 0))
        if capacity < 0 or load < 0:
            raise HTTPException(422, "Capacidad y carga deben ser no negativas")
    return payload

@app.get("/health")
def health():
    return {"status": "ok", "service": "DataCenter Command OS API", "version": app.version}

@app.get("/api")
def api_index():
    return {"resources": ["/api/" + name for name in RESOURCES], "docs": "/docs"}

@app.get("/api/{resource}")
def list_records(resource: str, limit: int = Query(default=200, ge=1, le=1000), offset: int = Query(default=0, ge=0)):
    if resource not in RESOURCES:
        raise HTTPException(404, "Recurso no encontrado")
    model, _ = RESOURCES[resource]
    with SessionLocal() as db:
        rows = db.scalars(select(model).order_by(model.id).offset(offset).limit(limit)).all()
        return {"items": [serialize(row) for row in rows], "limit": limit, "offset": offset}

@app.get("/api/{resource}/{record_id}")
def get_record(resource: str, record_id: int):
    if resource not in RESOURCES:
        raise HTTPException(404, "Recurso no encontrado")
    model, _ = RESOURCES[resource]
    with SessionLocal() as db:
        obj = db.get(model, record_id)
        if not obj:
            raise HTTPException(404, "Registro no encontrado")
        return serialize(obj)

@app.post("/api/{resource}", status_code=201)
def create_record(resource: str, record: RecordIn):
    if resource not in RESOURCES:
        raise HTTPException(404, "Recurso no encontrado")
    model, allowed = RESOURCES[resource]
    payload = validate_payload(resource, record.data, None) if resource != "equipment" else record.data
    with SessionLocal() as db:
        validate_payload(resource, payload, db)
        obj = model(**payload)
        db.add(obj)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(409, "No se pudo guardar. Revisa duplicados, referencias y tipos de datos.") from exc
        db.refresh(obj)
        return serialize(obj)

@app.patch("/api/{resource}/{record_id}")
def update_record(resource: str, record_id: int, record: RecordIn):
    if resource not in RESOURCES:
        raise HTTPException(404, "Recurso no encontrado")
    model, allowed = RESOURCES[resource]
    with SessionLocal() as db:
        obj = db.get(model, record_id)
        if not obj:
            raise HTTPException(404, "Registro no encontrado")
        payload = dict(record.data)
        validate_payload(resource, payload, db, exclude_id=record_id)
        for key, value in payload.items():
            setattr(obj, key, value)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(409, "No se pudo actualizar el registro.") from exc
        db.refresh(obj)
        return serialize(obj)

@app.delete("/api/{resource}/{record_id}", status_code=204)
def delete_record(resource: str, record_id: int):
    if resource not in RESOURCES:
        raise HTTPException(404, "Recurso no encontrado")
    model, _ = RESOURCES[resource]
    with SessionLocal() as db:
        obj = db.get(model, record_id)
        if not obj:
            raise HTTPException(404, "Registro no encontrado")
        db.delete(obj)
        db.commit()
    return None
