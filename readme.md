# Distributed Rate Limiting Infrastructure

A **Redis-backed distributed token-bucket rate limiter** built with FastAPI and Redis, designed for horizontally scalable API instances.

## Architecture

```text
Client
   │
   ▼
FastAPI
   │
   ▼
Redis
```

Multiple FastAPI instances share rate-limit state through Redis, allowing the application layer to scale horizontally without keeping rate-limit state in process memory.

## Features

* Token Bucket rate limiting
* Redis-backed shared state
* Atomic token refill and consumption using Redis Lua
* FastAPI API
* Docker Compose
* Prometheus metrics
* Grafana dashboard
* Health check endpoint
* Automated tests with pytest
* GitHub Actions CI

## How It Works

Each client is assigned a token bucket stored in Redis.

The default bucket configuration is:

| Setting          |          Value |
| ---------------- | -------------: |
| Bucket capacity  |       5 tokens |
| Refill rate      | 1 token/second |
| Cost per request |        1 token |

When a request arrives:

1. The current bucket state is retrieved from Redis.
2. Tokens are refilled based on the elapsed time.
3. One token is consumed if available.
4. If no token is available, the API returns **HTTP 429 Too Many Requests**.
5. The updated bucket state is stored back in Redis.

The refill, availability check, and token consumption are executed inside a **Redis Lua script**. This makes the entire operation atomic and prevents race conditions when multiple API instances process requests concurrently.

## Monitoring

The application exposes Prometheus metrics at:

```text
/metrics
```

Prometheus periodically scrapes this endpoint and stores the resulting time-series data.

Grafana connects to Prometheus to query and visualize these metrics through dashboards.

### Key Metrics

* `rate_limiter_requests_total` — total requests processed by the rate limiter
* `rate_limiter_rejected_total` — requests rejected because the rate limit was exceeded

### Monitoring Flow

```text
FastAPI
   │
   │ exposes /metrics
   ▼
Prometheus
   │
   │ PromQL queries
   ▼
Grafana
```

The Python Prometheus client maintains application-side metric objects and exposes them in Prometheus exposition format. It does **not** push metrics directly to Prometheus; Prometheus pulls the metrics by scraping `/metrics`.

## Running the Project

### Using Docker Compose

Build and start the complete stack:

```bash
docker compose up --build
```

The services will be available at:

| Service    | URL                   |
| ---------- | --------------------- |
| API        | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana    | http://localhost:3000 |

### Running Tests

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest
```

## CI

GitHub Actions automatically:

1. Sets up the Python environment
2. Installs project dependencies
3. Starts a Redis service
4. Runs the pytest test suite

The workflow is defined in:

```text
.github/workflows/ci.yml
```

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── rate_limiter.py
│   ├── rate_limit.lua
│   └── redis_client.py
├── tests/
│   └── test_rate_limiter.py
├── prometheus.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml
```

## Design Highlights

### Redis as Shared State

Rate-limit state is stored in Redis rather than application memory. This allows multiple FastAPI instances to enforce the same limits.

```text
             ┌─────────────┐
Client ─────►│  FastAPI 1  │──┐
             └─────────────┘  │
                              ▼
             ┌─────────────┐ Redis
Client ─────►│  FastAPI 2  │──┤
             └─────────────┘  │
                              │
             ┌─────────────┐  │
Client ─────►│  FastAPI 3  │──┘
             └─────────────┘
```

### Atomic Rate-Limit Operations

The Redis Lua script performs token refill, limit checking, and consumption as a single atomic operation.

This prevents two concurrent requests from observing the same token and both consuming it.

## Technology Stack

* **Python**
* **FastAPI**
* **Redis**
* **Redis Lua**
* **Docker / Docker Compose**
* **Prometheus**
* **Grafana**
* **pytest**
* **GitHub Actions**

## Why Redis Lua?

A rate limiter needs the refill and consume operations to behave atomically.

Without atomic execution, concurrent requests could potentially:

```text
Request A → Read 1 token
Request B → Read 1 token
Request A → Consume token
Request B → Consume token
```

Both requests could incorrectly succeed.

With the Redis Lua script, the complete operation executes atomically inside Redis, ensuring that concurrent requests cannot interleave these operations.

## Summary

This project demonstrates a **Redis-backed distributed rate limiter** designed for horizontally scalable API instances, with atomic rate-limit enforcement, containerized deployment, automated testing, and Prometheus/Grafana observability.
