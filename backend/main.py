
import logging
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr

from .database import engine, SessionLocal, Base
from . import models
from .auth import hash_password, verify_password

# Import ML prediction function
try:
    from ml.predict_url import predict_url
except Exception as e:
    predict_url = None
    logging.getLogger("uvicorn.error").exception(
        "Failed to import ML predict_url: %s", e
    )

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PhishGuard Backend (FastAPI + ML + Auth)")

# CORS (Development Mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PredictRequest(BaseModel):
    url: str
    user_id: int



@app.get("/")
def home():
    return {"message": "PhishGuard Backend running"}


# Signup

@app.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.User).filter(models.User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(data.password)

        user = models.User(
            name=data.name,
            email=data.email,
            password=hashed
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "User created successfully", "user_id": user.id}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        db.rollback()
        logger.exception("Signup error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Login

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    try:
        user = db.query(models.User).filter(models.User.email == data.email).first()

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "message": "Login successful",
            "user_id": user.id,
            "name": user.name,
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Predict (Updated Logic)

@app.post("/predict")
def predict(data: PredictRequest, db: Session = Depends(get_db)):

    try:
        if predict_url is None:
            raise HTTPException(status_code=500, detail="ML model not available")

        # Call updated ML logic
        result = predict_url(data.url)

        prediction_label = result["prediction"]
        confidence = result["confidence"]
        risk_score = result["risk_score"]
        risk_level = result["risk_level"]

        # Save scan history
        scan = models.ScanHistory(
            user_id=data.user_id,
            url=result["url"],
            prediction=prediction_label,
            confidence=confidence,
            risk_score=risk_score
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "anti_phishing_score": result.get("anti_phishing_score", 0),
            "shap_values": result["shap_values"],
            "base_value": result["base_value"]
        }

    except Exception as e:
        db.rollback()
        logger.exception("Prediction error: %s", e)
        raise HTTPException(status_code=500, detail="Prediction failed")


# Scan History

@app.get("/scan-history/{user_id}")
def get_scan_history(user_id: int, db: Session = Depends(get_db)):


    try:
        history = (
            db.query(models.ScanHistory)
            .filter(models.ScanHistory.user_id == user_id)
            .order_by(models.ScanHistory.scanned_at.desc())
            .all()
        )

        return [
            {
                "id": h.id,
                "url": h.url,
                "prediction": h.prediction,
                "confidence": h.confidence,
                "risk_score": h.risk_score,
                "scanned_at": h.scanned_at
            }
            for h in history
        ]

    except Exception as e:
        logger.exception("History fetch error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch scan history")
    
@app.post("/predict-extension")
def predict_extension(data: dict):

    url = data.get("url")

    if not url:
        raise HTTPException(status_code=400, detail="URL required")

    result = predict_url(url)
    return result