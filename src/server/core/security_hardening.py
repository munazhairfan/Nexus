import re
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List

def sanitize_input(text: str) -> str:
    # Strip HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit=60, window_seconds=60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.cache: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.cache:
            self.cache[client_ip] = []

        # Prune old timestamps
        self.cache[client_ip] = [t for t in self.cache[client_ip] if current_time - t < self.window_seconds]

        if len(self.cache[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Rate limit exceeded."
            )

        self.cache[client_ip].append(current_time)
        return await call_next(request)
