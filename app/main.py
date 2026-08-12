from fastapi import FastAPI, HTTPException, Request

from app.redis_client import redis_client
from app.rate_limiter import RateLimiter

from prometheus_client import Counter, generate_latest
from fastapi.responses import Response


app = FastAPI()

rate_limiter = RateLimiter(
    redis_client=redis_client,
    capacity=5,
    refill_rate=1
)

requests_total = Counter(
    "rate_limiter_requests_total",
    "Total number of requests"
)

requests_rejected = Counter(
    "rate_limiter_rejected_total",
    "Total number of rate-limited requests"
)

@app.get("/")
def root():
    return {"message": "Rate limiter is running"}


@app.get("/api/data")
def get_data(request: Request):
    requests_total.inc()
    client_ip = request.client.host

    if not rate_limiter.allow_request(client_ip):
        requests_rejected.inc()
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    return {"message": "Here is your data"}

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

@app.get("/health")
def health():
    return {"status": "healthy"}