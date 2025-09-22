import time
import os
from typing import Dict, List
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimiter:
    
    def __init__(self) -> None:
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < window_seconds]
        
        if len(self.requests[key]) >= max_requests:
            return False
        
        self.requests[key].append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, limiter: InMemoryRateLimiter):
        super().__init__(app)
        self.limiter = limiter
    
    async def dispatch(self, request: Request, call_next):
        if os.getenv("LOG_LEVEL") == "warning":
            return await call_next(request)
            
        if request.url.path in ["/v1/users", "/v1/users/activate"]:
            client_ip = request.client.host if request.client else "unknown"
            
            if request.url.path == "/v1/users":
                if not self.limiter.is_allowed(f"reg:{client_ip}", 100, 3600):
                    raise HTTPException(429, "Too many registration attempts. Try again later.")
            
            elif request.url.path == "/v1/users/activate":
                if not self.limiter.is_allowed(f"act:{client_ip}", 50, 3600):
                    raise HTTPException(429, "Too many activation attempts. Try again later.")
        
        return await call_next(request)
