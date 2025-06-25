from flask import request, abort
import re
import time
from functools import wraps

# Simple in-memory rate limiter per IP
RATE_LIMIT = {}
MAX_REQUESTS = 100  # requests
TIME_WINDOW = 60    # seconds

# Common scraper User-Agents
BLOCKED_USER_AGENTS = [
    'python', 'scrapy', 'curl', 'wget', 'java', 'httpclient', 'bot', 'crawler'
]

# IP Blacklist (manually or dynamically extendable)
BLOCKED_IPS = set()

# Regex pattern for basic XSS detection
XSS_PATTERN = re.compile(r'<script.*?>.*?</script.*?>', re.IGNORECASE)

def protect_route(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr or "unknown"

        # Block known bad IPs
        if ip in BLOCKED_IPS:
            abort(403, "Forbidden: Your IP is blocked")

        # Block suspicious User-Agents
        ua = (request.headers.get("User-Agent") or "").lower()
        for bad in BLOCKED_USER_AGENTS:
            if bad in ua:
                abort(403, "Forbidden: Suspicious User-Agent")

        # Rate limiting (per IP)
        now = time.time()
        RATE_LIMIT.setdefault(ip, [])
        RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < TIME_WINDOW]

        if len(RATE_LIMIT[ip]) >= MAX_REQUESTS:
            abort(429, "Too Many Requests: Slow down")

        RATE_LIMIT[ip].append(now)

        # Basic input filtering (XSS attempt)
        for value in request.values.values():
            if XSS_PATTERN.search(value):
                abort(400, "Bad Request: Potential XSS detected")

        return f(*args, **kwargs)
    return decorated_function