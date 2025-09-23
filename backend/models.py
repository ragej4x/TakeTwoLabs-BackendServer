from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(index=True, unique=True)
    customerName: str = ""
    customerPhone: str
    customerEmail: str = ""
    deliveryAddress: str
    itemDescription: str = ""
    shoeCondition: str = ""
    shoeService: Optional[str] = None
    waiverSigned: bool = False
    waiverUrl: Optional[str] = None
    beforePhotos: str = "[]"  # JSON string list
    assignedTo: Optional[str] = None
    needsReglue: Optional[bool] = None
    needsPaint: Optional[bool] = None
    status: str = "pending"
    serviceDetails: Optional[str] = None  # JSON string
    afterPhotos: str = "[]"  # JSON string list
    billing: Optional[float] = None
    additionalBilling: Optional[float] = None
    deliveryOption: Optional[str] = None
    markedAs: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


