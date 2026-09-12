from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "Model_pipeline.pkl"

app = FastAPI(
    title="NYC Airbnb Room Type Predictor",
    description="Predicts whether an NYC Airbnb listing is an entire home, "
    "a private room, or a shared room.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

COLUMNS = [
    "latitude",
    "longitude",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
    "neighbourhood_group",
    "neighbourhood",
]

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError as exc: 
    raise RuntimeError(
        f"Could not find the trained model at {MODEL_PATH}. "
        "Make sure model/Model_pipeline.pkl is present."
    ) from exc


class Features(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    price: float = Field(..., gt=0, description="Price per night, must be positive")
    minimum_nights: int = Field(..., ge=1, le=365, description="Minimum nights required for booking")
    number_of_reviews: int = Field(..., ge=0, description="Total number of reviews")
    reviews_per_month: float = Field(..., ge=0, description="Average reviews per month")
    calculated_host_listings_count: int = Field(..., ge=0, description="Number of listings by this host")
    availability_365: int = Field(..., ge=0, le=365, description="Days available out of 365")
    neighbourhood_group: str = Field(..., min_length=1, description="Borough or neighbourhood group")
    neighbourhood: str = Field(..., min_length=1, description="Specific neighbourhood name")


class PredictionResponse(BaseModel):
    Predicted_room_type: str
    Probability: list[float]


NAV_ITEMS = [
    {"label": "Home", "path": "/"},
    {"label": "About", "path": "/about"},
    {"label": "Projects", "path": "/projects"},
    {"label": "Contact", "path": "/contact"},
]


@app.get("/", response_class=templates.TemplateResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"nav_items": NAV_ITEMS, "active": "/"},
    )


@app.get("/about", response_class=templates.TemplateResponse, include_in_schema=False)
def about(request: Request):
    return templates.TemplateResponse(
        request,
        "about.html",
        {"nav_items": NAV_ITEMS, "active": "/about"},
    )


@app.get("/projects", response_class=templates.TemplateResponse, include_in_schema=False)
def projects(request: Request):
    return templates.TemplateResponse(
        request,
        "projects.html",
        {"nav_items": NAV_ITEMS, "active": "/projects"},
    )


@app.get("/contact", response_class=templates.TemplateResponse, include_in_schema=False)
def contact(request: Request):
    return templates.TemplateResponse(
        request,
        "contact.html",
        {"nav_items": NAV_ITEMS, "active": "/contact"},
    )


@app.get("/api/health", tags=["api"])
def health():
    """Simple liveness check used by the front end to show API status."""
    return {"status": "ok"}


@app.post("/api/predict", response_model=PredictionResponse, tags=["api"])
def predict(features: Features):
    try:
        row = pd.DataFrame([features.dict()], columns=COLUMNS)
        prediction = model.predict(row)
        probability = model.predict_proba(row)
    except Exception as exc:  
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return {
        "Predicted_room_type": prediction[0],
        "Probability": probability.tolist()[0],
    }
