import time


class RateLimiter:

    def __init__(self, redis_client, capacity, refill_rate):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

        with open("app/rate_limit.lua", "r") as file:
            self.script = self.redis.register_script(file.read())

    def allow_request(self, client_id):

        key = f"rate_limit:{client_id}"

        result = self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                time.time()
            ]
        )

        return bool(result)