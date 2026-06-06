from fastapi import FastAPI, Request
from starlette.responses import Response
import json
import math

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


def p95(values):
    values = sorted(values)
    if not values:
        return 0
    idx = math.ceil(0.95 * len(values)) - 1
    return values[idx]


@app.options("/")
async def options_handler():
    return Response(content="", headers=CORS_HEADERS)


@app.post("/")
async def analytics(request: Request):
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

    return Response(
        content=json.dumps(result),
        media_type="application/json",
        headers=CORS_HEADERS
    )
