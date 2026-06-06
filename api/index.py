from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import math

app = FastAPI()

# ✅ CORS (this is required for grader)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load dataset
with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


def p95(values):
    if not values:
        return 0
    values = sorted(values)
    idx = math.ceil(0.95 * len(values)) - 1
    return values[idx]


@app.post("/")
async def analytics(request: Request):
    body = await request.json()

    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        filtered = [x for x in DATA if x["region"] == region]

        latencies = [x["latency_ms"] for x in filtered]
        uptimes = [x["uptime_pct"] for x in filtered]

        if not latencies:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": len([x for x in latencies if x > threshold])
        }

    return JSONResponse(
        content=result,
        headers={"Access-Control-Allow-Origin": "*"}
    )
