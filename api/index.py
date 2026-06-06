# api/index.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import json
import numpy as np

app = FastAPI()

# Enable CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Request model

class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: int

# Load telemetry file once

with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

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
        uptimes = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > data.threshold_ms
            )
        }

    return result
