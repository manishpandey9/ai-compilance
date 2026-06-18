"""Admin authentication dependency."""

from fastapi import Header, HTTPException

from app.config import settings


async def require_admin(x_admin_key: str = Header(..., alias="X-Admin-Key")) -> str:
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "forbidden", "message": "Invalid admin key", "details": []}},
        )
    return x_admin_key
