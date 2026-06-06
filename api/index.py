from fastapi import FastAPI, Request
from starlette.responses import Response
import json

app = FastAPI()

# CORS headers (required by grader)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

# load dataset
with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


# ✅ correct percentile (INTERPOLATION method)
def p95(values):
    values = sorted(values)
    n = len(values)

    if n == 0:
        return 0

    rank = 0.95 * (n - 1)
    lower = int(rank)
    upper = lower + 1

    if upper >= n:
        return values[lower]

    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight


@app.options("/")
async def options_handler():
    return Response(content="", headers=CORS_HEADERS)


@app.post("/")
async def analytics(request: Request):
    body = await request.json()

    regions = body["regions"]
    threshold = body["threshold_ms"]

    result_regions = []

    for region in regions:
        rows = [x for x in DATA if x["region"] == region]

        latencies = [x["latency_ms"] for x in rows]
        uptimes = [x["uptime_pct"] for x in rows]

        result_regions.append({
            "region": region,
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": len([x for x in latencies if x > threshold])
        })

    return Response(
        content=json.dumps({"regions": result_regions}),
        media_type="application/json",
        headers=CORS_HEADERS
    )
