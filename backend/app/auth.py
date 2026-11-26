import os
import threading
import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JOSEError, JWTError, jwt

bearer_scheme = HTTPBearer(auto_error=False)
_jwks_lock = threading.Lock()
_jwks_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_JWKS_CACHE_SECONDS = 600
_ALLOWED_ASYMMETRIC_ALGORITHMS = {"ES256", "RS256"}


def _supabase_url() -> str:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not url:
        raise HTTPException(503, "Supabase authentication is not configured")
    if (os.getenv("APP_ENV", "").lower() == "production" or os.getenv("VERCEL") == "1") \
            and not url.startswith("https://"):
        raise HTTPException(503, "Supabase authentication must use HTTPS in production")
    return url


def _jwks_for(url: str) -> dict[str, Any]:
    jwks_url = f"{url}/auth/v1/.well-known/jwks.json"
    now = time.monotonic()
    with _jwks_lock:
        cached = _jwks_cache.get(jwks_url)
        if cached and now - cached[0] < _JWKS_CACHE_SECONDS:
            return cached[1]
        try:
            response = httpx.get(jwks_url, timeout=5.0)
            response.raise_for_status()
            keys = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise HTTPException(503, "Unable to verify Supabase signing keys") from error
        if not isinstance(keys, dict) or not isinstance(keys.get("keys"), list):
            raise HTTPException(503, "Supabase returned an invalid signing-key set")
        _jwks_cache[jwks_url] = (now, keys)
        return keys


def _signing_key(token: str, url: str) -> tuple[Any, str]:
    try:
        header = jwt.get_unverified_header(token)
    except JOSEError as error:
        raise HTTPException(401, "Invalid bearer token") from error

    algorithm = header.get("alg")
    if algorithm == "HS256":
        secret = os.getenv("SUPABASE_JWT_SECRET")
        if not secret:
            raise HTTPException(503, "Supabase HS256 verification is not configured")
        return secret, algorithm

    if algorithm not in _ALLOWED_ASYMMETRIC_ALGORITHMS:
        raise HTTPException(401, "Unsupported bearer-token signing algorithm")
    kid = header.get("kid")
    if not isinstance(kid, str):
        raise HTTPException(401, "Bearer token has no signing-key ID")
    matching_keys = [
        key for key in _jwks_for(url).get("keys", [])
        if key.get("kid") == kid
        and key.get("use", "sig") == "sig"
        and key.get("alg", algorithm) == algorithm
    ]
    if len(matching_keys) != 1:
        raise HTTPException(401, "Bearer token signing key was not found")
    return matching_keys[0], algorithm


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    url = _supabase_url()
    signing_key, algorithm = _signing_key(credentials.credentials, url)
    issuer = f"{url}/auth/v1"
    try:
        claims = jwt.decode(
            credentials.credentials,
            signing_key,
            algorithms=[algorithm],
            audience="authenticated",
            issuer=issuer,
            options={"require_exp": True, "require_sub": True},
        )
    except (JOSEError, TypeError, ValueError) as error:
        raise HTTPException(401, "Invalid or expired bearer token",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    if claims.get("role") != "authenticated" or claims.get("is_anonymous") is True \
            or not isinstance(claims.get("sub"), str) or not claims["sub"]:
        raise HTTPException(401, "A signed-in Supabase user is required",
                            headers={"WWW-Authenticate": "Bearer"})
    return claims
