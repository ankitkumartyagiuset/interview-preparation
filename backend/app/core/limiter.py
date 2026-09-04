import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.core.config import settings

class RateLimiter:
    """Sliding-window rate limiter with in-memory storage."""
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        current_time = time.time()
        window_start = current_time - 60.0
        
        key = f"{client_ip}:{endpoint}"
        # Filter timestamps outside the sliding window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        if len(self.requests[key]) >= self.rpm:
            return False
        
        self.requests[key].append(current_time)
        return True

rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

async def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting sensitive endpoints."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    endpoint = request.url.path
    
    allowed = rate_limiter.check_rate_limit(client_ip, endpoint)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before trying again."
        )
