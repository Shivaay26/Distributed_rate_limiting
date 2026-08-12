from fastapi import FastAPI, HTTPException, Request

from app.redis_client import redis_client
from app.rate_limiter import RateLimiter


app = FastAPI()

rate_limiter = RateLimiter(
    redis_client=redis_client,
    capacity=5,
    refill_rate=1
)


@app.get("/")
def root():
    return {"message": "Rate limiter is running"}


@app.get("/api/data")
def get_data(request: Request):

    client_ip = request.client.host

    if not rate_limiter.allow_request(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    return {"message": "Here is your data"}