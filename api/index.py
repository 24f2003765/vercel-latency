from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import math

app = FastAPI()

# CORS (required)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load data safely
with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


def p95(values):
    if not values:
        return 0
    values = sorted(values)
    idx = math.ceil(0.95 * len(values)) - 1
    return values[idx]


@app.options("/")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.post("/")
async def analytics(request: Request):
    try:
        body = await request.json()

        regions = body["regions"]
        threshold = body["threshold_ms"]

        result = {}

        for region in regions:
            rows = [x for x in DATA if x["region"] == region]

            latencies = [x["latency_ms"] for x in rows]
            uptimes = [x["uptime_pct"] for x in rows]

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

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )
