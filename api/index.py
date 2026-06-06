# api/index.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import json
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Request body model

class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: int

# Load telemetry file

DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)

# Optional GET route so visiting the URL in a browser works

@app.get("/")
def home():
    return {"message": "Latency Analytics API is running"}

# Required POST endpoint

@app.post("/")
def analyse(data: RequestData):

    result = {}

    for region in data.regions:

        rows = [
            r for r in telemetry
            if r["region"] == region
        ]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for latency in latencies
                if latency > data.threshold_ms
            )
        }

    return result
