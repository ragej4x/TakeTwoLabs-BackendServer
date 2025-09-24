from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import json
# Environment variables should be set in the shell before running

from sqlmodel import select
from db import init_db, get_session
from models import Entry as EntryModel, User as UserModel
from auth import get_password_hash, verify_password, create_access_token, get_current_user_email
import secrets
import smtplib
from email.mime.text import MIMEText
from sqlmodel import Session
from storage import get_supabase


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
    waiverUrl: Optional[str] = None
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"])

# Serve local uploaded files (if not using external storage)
from starlette.staticfiles import StaticFiles
from pathlib import Path
UPLOADS_DIR = Path(__file__).with_name("uploads")
try:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


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
            waiverUrl=r.waiverUrl,
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
        waiverUrl=payload.waiverUrl,
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
        waiverUrl=row.waiverUrl,
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
    waiverUrl: Optional[str] = None
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
        waiverUrl=row.waiverUrl,
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


class UploadInitResponse(BaseModel):
    url: str


@app.post("/upload", response_model=dict)
def upload_file(filename: str, current_user: str = Depends(get_current_user_email)) -> dict:
    # Client will PUT directly to Supabase storage using the public bucket
    # For simplicity, we will upload via server here synchronously
    supabase = get_supabase()
    bucket = os.environ.get("SUPABASE_BUCKET", "uploads")
    # Expecting base64 in body would be heavy; keep it simple with presigned URL later.
    # For MVP, just return bucket/path for client-side direct upload via supabase-js (optional).
    return {"bucket": bucket, "path": f"{current_user}/{filename}"}


# Upload waiver PDF to Supabase and return a public URL
@app.post("/upload/waiver", response_model=dict)
async def upload_waiver(request: Request, file: UploadFile = File(...), current_user: str = Depends(get_current_user_email)) -> dict:
    # Verify required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_BUCKET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    try:
        print(f"Processing upload for user: {current_user}")
        print(f"File name: {file.filename}")
        ts = int(datetime.utcnow().timestamp())
        safe_name = file.filename.replace("/", "_").replace("\\", "_")
        file_path = f"waivers/{current_user}/{ts}_{safe_name}"
        
        # Read file content
        content = await file.read()
        
        # Upload to Supabase storage
        print("Initializing Supabase client...")
        supabase = get_supabase()
        bucket_name = "uploads"  # Use fixed bucket name
        print(f"Using bucket: {bucket_name}")
        
        # Ensure bucket exists
        try:
            print("Checking/creating bucket...")
            # Try to get bucket info first
            try:
                supabase.storage.get_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' already exists")
            except Exception:
                print(f"Bucket '{bucket_name}' not found, creating...")
                supabase.storage.create_bucket(bucket_name, {"public": True})
                print("Bucket created successfully")
        except Exception as e:
            print(f"Error with bucket operation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Storage bucket error: {str(e)}"
            )
            
        try:
            # Upload the file
            print(f"Uploading file to path: {file_path}")
            print(f"Uploading file to '{file_path}'...")
            # Remove any existing file
            try:
                supabase.storage.from_(bucket_name).remove([file_path])
                print("Removed existing file if any")
            except Exception:
                pass  # Ignore if file doesn't exist
                
            # Upload new file
            res = supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=content,
                file_options={"content-type": "application/pdf"}
            )
            print("File uploaded successfully")
            print("Upload successful")
            
            # Get the public URL
            print("Getting public URL...")
            # Generate signed URL that expires in 7 days
            signed_url = supabase.storage\
                .from_(bucket_name)\
                .create_signed_url(file_path, 604800)  # 7 days in seconds
            
            if not signed_url or 'signedURL' not in signed_url:
                raise HTTPException(status_code=500, detail="Failed to generate signed URL")
                
            print(f"Signed URL generated: {signed_url['signedURL']}")
            return {"url": signed_url['signedURL']}
        except Exception as upload_error:
            print(f"Upload operation failed: {str(upload_error)}")
            raise upload_error
        
    except Exception as e:
        import traceback
        print(f"Upload failed. Error: {str(e)}")
        print("Detailed traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


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


@app.post("/auth/register", response_model=dict)
def register(req: RegisterRequest, session: Session = Depends(get_session)) -> dict:
    exists = session.exec(select(UserModel).where(UserModel.email == req.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    # create user as unverified
    user = UserModel(
        email=req.email,
        password_hash=get_password_hash(req.password),
        first_name=req.first_name,
        last_name=req.last_name,
        phone=req.phone,
        verified=False,
    )
    session.add(user)
    session.commit()
    # create verification token
    token = secrets.token_urlsafe(32)
    # store token temporarily in user.phone field if empty (simple MVP); prefer a separate table in prod
    user.phone = f"verify:{token}"
    session.add(user)
    session.commit()
    # send email via Gmail SMTP
    try:
        app_password = os.environ.get("GMAIL_APP_PASSWORD", "gfzf hypn onya rokb")
        sender = "jimboyaczon@taketwomanila.com"
        recipient = "info@taketwomanila.com"  # Admin’s email

        verify_link = f"http://127.0.0.1:8000/auth/verify?token={token}&email={req.email}"

        body = f"""\
        New User Registration Pending Verification – TakeTwoLabs

        A new user has registered and is awaiting your confirmation.

        User Details:
        - Name: {req.first_name or ""} {req.last_name or ""}
        - Email: {req.email}

        To verify and activate this account, please click the link below:
        {verify_link}

        If this registration looks suspicious, you may safely ignore this request.

        Thanks,
        The TakeTwoLabs System
        """


        msg = MIMEText(body)
        msg["Subject"] = "New User Registration Pending Verification – TakeTwoLabs"
        msg["From"] = sender
        msg["To"] = recipient
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.sendmail(sender, [recipient], msg.as_string())
    except Exception as e:
        # Do not expose internal error, but log/print server side
        print("Email send failed:", e)
    return {"message": "Registration successful. Please check your email to verify your account."}


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = session.exec(select(UserModel).where(UserModel.email == req.email)).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.verified:
        raise HTTPException(status_code=403, detail="Account not verified. Please check your email.")
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@app.get("/auth/verify")
def verify_email(token: str, email: str, session: Session = Depends(get_session)):
    user = session.exec(select(UserModel).where(UserModel.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # simple check: token stored in phone as "verify:<token>"
    expected = f"verify:{token}"
    if user.phone != expected:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.verified = True
    # clear token storage placeholder
    user.phone = None
    session.add(user)
    session.commit()
    return {"verified": True}


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


