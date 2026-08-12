import time
import redis


class RateLimiter:

    def __init__(self, redis_client, capacity, refill_rate):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

    def allow_request(self, client_id):

        key = f"rate_limit:{client_id}"

        data = self.redis.hgetall(key)

        if not data:
            tokens = self.capacity
            last_refill = time.time()
        else:
            tokens = float(data["tokens"])
            last_refill = float(data["last_refill"])

        now = time.time()

        elapsed = now - last_refill

        tokens = min(
            self.capacity,
            tokens + elapsed * self.refill_rate
        )

        if tokens < 1:
            return False

        tokens -= 1

        self.redis.hset(
            key,
            mapping={
                "tokens": tokens,
                "last_refill": now
            }
        )

        return True