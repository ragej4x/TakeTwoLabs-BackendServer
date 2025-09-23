from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import json

from sqlmodel import select
from .db import init_db, get_session
from .models import Entry as EntryModel, User as UserModel
from .auth import get_password_hash, verify_password, create_access_token, get_current_user_email
from sqlmodel import Session


class ServiceDetails(BaseModel):
    isShoeClean: Optional[str] = None
    serviceType: Optional[str] = None
    needsReglue: Optional[bool] = None
    needsPaint: Optional[bool] = None
    qcPassed: Optional[bool] = None
    basicCleaning: Optional[str] = None
    receivedBy: Optional[str] = None


class EntryCreate(BaseModel):
    customerName: str = ""
    customerPhone: str
    customerEmail: str = ""
    deliveryAddress: str
    itemDescription: str = ""
    shoeCondition: str = ""
    shoeService: Optional[str] = None
    waiverSigned: bool = False
    beforePhotos: List[str] = Field(default_factory=list)
    assignedTo: Optional[str] = None
    needsReglue: Optional[bool] = None
    needsPaint: Optional[bool] = None
    status: str = Field(default="pending")
    serviceDetails: Optional[ServiceDetails] = None
    afterPhotos: List[str] = Field(default_factory=list)
    billing: Optional[float] = None
    additionalBilling: Optional[float] = None
    deliveryOption: Optional[str] = None
    markedAs: Optional[str] = None


class Entry(EntryCreate):
    id: str
    createdAt: datetime
    updatedAt: datetime


app = FastAPI(title="TakeTwoLabs Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/entries", response_model=List[Entry])
def list_entries(current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> List[Entry]:
    rows = session.exec(select(EntryModel)).all()
    result: List[Entry] = []
    for r in rows:
        result.append(Entry(
            id=r.public_id,
            customerName=r.customerName,
            customerPhone=r.customerPhone,
            customerEmail=r.customerEmail,
            deliveryAddress=r.deliveryAddress,
            itemDescription=r.itemDescription,
            shoeCondition=r.shoeCondition,
            shoeService=r.shoeService,
            waiverSigned=r.waiverSigned,
            beforePhotos=json.loads(r.beforePhotos or "[]"),
            assignedTo=r.assignedTo,
            needsReglue=r.needsReglue,
            needsPaint=r.needsPaint,
            status=r.status,
            serviceDetails=json.loads(r.serviceDetails) if r.serviceDetails else None,
            afterPhotos=json.loads(r.afterPhotos or "[]"),
            billing=r.billing,
            additionalBilling=r.additionalBilling,
            deliveryOption=r.deliveryOption,
            markedAs=r.markedAs,
            createdAt=r.createdAt,
            updatedAt=r.updatedAt,
        ))
    return result


@app.post("/entries", response_model=Entry)
def create_entry(payload: EntryCreate, current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> Entry:
    now = datetime.utcnow()
    public_id = uuid.uuid4().hex
    row = EntryModel(
        public_id=public_id,
        customerName=payload.customerName,
        customerPhone=payload.customerPhone,
        customerEmail=payload.customerEmail,
        deliveryAddress=payload.deliveryAddress,
        itemDescription=payload.itemDescription,
        shoeCondition=payload.shoeCondition,
        shoeService=payload.shoeService,
        waiverSigned=payload.waiverSigned,
        beforePhotos=json.dumps(payload.beforePhotos or []),
        assignedTo=payload.assignedTo,
        needsReglue=payload.needsReglue,
        needsPaint=payload.needsPaint,
        status=payload.status,
        serviceDetails=json.dumps(payload.serviceDetails.dict() if payload.serviceDetails else None) if payload.serviceDetails else None,
        afterPhotos=json.dumps(payload.afterPhotos or []),
        billing=payload.billing,
        additionalBilling=payload.additionalBilling,
        deliveryOption=payload.deliveryOption,
        markedAs=payload.markedAs,
        createdAt=now,
        updatedAt=now,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return Entry(
        id=row.public_id,
        customerName=row.customerName,
        customerPhone=row.customerPhone,
        customerEmail=row.customerEmail,
        deliveryAddress=row.deliveryAddress,
        itemDescription=row.itemDescription,
        shoeCondition=row.shoeCondition,
        shoeService=row.shoeService,
        waiverSigned=row.waiverSigned,
        beforePhotos=json.loads(row.beforePhotos or "[]"),
        assignedTo=row.assignedTo,
        needsReglue=row.needsReglue,
        needsPaint=row.needsPaint,
        status=row.status,
        serviceDetails=json.loads(row.serviceDetails) if row.serviceDetails else None,
        afterPhotos=json.loads(row.afterPhotos or "[]"),
        billing=row.billing,
        additionalBilling=row.additionalBilling,
        deliveryOption=row.deliveryOption,
        markedAs=row.markedAs,
        createdAt=row.createdAt,
        updatedAt=row.updatedAt,
    )


class EntryUpdate(BaseModel):
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    customerEmail: Optional[str] = None
    deliveryAddress: Optional[str] = None
    itemDescription: Optional[str] = None
    shoeCondition: Optional[str] = None
    shoeService: Optional[str] = None
    waiverSigned: Optional[bool] = None
    beforePhotos: Optional[List[str]] = None
    assignedTo: Optional[str] = None
    needsReglue: Optional[bool] = None
    needsPaint: Optional[bool] = None
    status: Optional[str] = None
    serviceDetails: Optional[ServiceDetails] = None
    afterPhotos: Optional[List[str]] = None
    billing: Optional[float] = None
    additionalBilling: Optional[float] = None
    deliveryOption: Optional[str] = None
    markedAs: Optional[str] = None


@app.patch("/entries/{entry_id}", response_model=Entry)
def update_entry(entry_id: str, updates: EntryUpdate, current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> Entry:
    row = session.exec(select(EntryModel).where(EntryModel.public_id == entry_id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    data = updates.dict(exclude_unset=True)
    if "beforePhotos" in data:
        row.beforePhotos = json.dumps(data.pop("beforePhotos") or [])
    if "afterPhotos" in data:
        row.afterPhotos = json.dumps(data.pop("afterPhotos") or [])
    if "serviceDetails" in data and data["serviceDetails"] is not None:
        row.serviceDetails = json.dumps(data.pop("serviceDetails"))
    for k, v in data.items():
        setattr(row, k, v)
    row.updatedAt = datetime.utcnow()
    session.add(row)
    session.commit()
    session.refresh(row)
    return Entry(
        id=row.public_id,
        customerName=row.customerName,
        customerPhone=row.customerPhone,
        customerEmail=row.customerEmail,
        deliveryAddress=row.deliveryAddress,
        itemDescription=row.itemDescription,
        shoeCondition=row.shoeCondition,
        shoeService=row.shoeService,
        waiverSigned=row.waiverSigned,
        beforePhotos=json.loads(row.beforePhotos or "[]"),
        assignedTo=row.assignedTo,
        needsReglue=row.needsReglue,
        needsPaint=row.needsPaint,
        status=row.status,
        serviceDetails=json.loads(row.serviceDetails) if row.serviceDetails else None,
        afterPhotos=json.loads(row.afterPhotos or "[]"),
        billing=row.billing,
        additionalBilling=row.additionalBilling,
        deliveryOption=row.deliveryOption,
        markedAs=row.markedAs,
        createdAt=row.createdAt,
        updatedAt=row.updatedAt,
    )


@app.delete("/entries/{entry_id}", response_model=dict)
def delete_entry(entry_id: str, current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> dict:
    row = session.exec(select(EntryModel).where(EntryModel.public_id == entry_id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    session.delete(row)
    session.commit()
    return {"deleted": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, session: Session = Depends(get_session)) -> TokenResponse:
    exists = session.exec(select(UserModel).where(UserModel.email == req.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = UserModel(
        email=req.email,
        password_hash=get_password_hash(req.password),
        first_name=req.first_name,
        last_name=req.last_name,
        phone=req.phone,
    )
    session.add(user)
    session.commit()
    token = create_access_token(subject=req.email)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = session.exec(select(UserModel).where(UserModel.email == req.email)).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


class MeResponse(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class MeUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@app.get("/me", response_model=MeResponse)
def get_me(current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> MeResponse:
    user = session.exec(select(UserModel).where(UserModel.email == current_user)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MeResponse(email=user.email, first_name=user.first_name, last_name=user.last_name, phone=user.phone)


@app.patch("/me", response_model=MeResponse)
def update_me(payload: MeUpdateRequest, current_user: str = Depends(get_current_user_email), session: Session = Depends(get_session)) -> MeResponse:
    user = session.exec(select(UserModel).where(UserModel.email == current_user)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(user, k, v)
    session.add(user)
    session.commit()
    session.refresh(user)
    return MeResponse(email=user.email, first_name=user.first_name, last_name=user.last_name, phone=user.phone)


