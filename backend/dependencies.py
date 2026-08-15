import os
import urllib.parse
from fastapi import HTTPException, status
from typing import List

def get_allowed_origins() -> List[str]:
    """Return list of allowed origins for CORS.
    Reads from environment variable ALLOWED_ORIGINS (comma separated).
    If not set, defaults to allow all origins (legacy behavior).
    """
    origins = os.getenv("ALLOWED_ORIGINS")
    if origins:
        return [origin.strip() for origin in origins.split(",") if origin.strip()]
    return ["*"]

def validate_url(url: str) -> str:
    """Simple SSRF protection: ensure URL has a network scheme and is not a local address.
    Raises HTTPException 400 if validation fails.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must use http or https scheme.")
    # Disallow loopback, private IPs, and localhost
    hostname = parsed.hostname or ""
    prohibited = ["localhost", "127.0.0.1", "::1"]
    if hostname in prohibited or hostname.endswith(".local"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to local network resources is prohibited.")
    return url
