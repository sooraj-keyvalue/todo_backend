"""
Health check router.
Provides liveness and readiness probe endpoints.
Can be expanded to include database connectivity checks, cache checks, etc.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Liveness probe endpoint.
    Returns 200 if the application is running.

    This endpoint should always return success if the application
    process is alive. It's used by orchestrators (like Kubernetes)
    to determine if the pod should be restarted.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """
    Readiness probe endpoint.
    Returns 200 if the application is ready to serve requests.

    This endpoint can be expanded to check:
    - Database connectivity
    - Cache availability
    - External service dependencies
    - Any other critical dependencies

    Currently returns a simple ready status.
    """
    return {"status": "ready"}


# Future expansion example:
# @router.get("/ready/detailed")
# async def detailed_readiness_check(
#     db: Session = Depends(get_db)
# ) -> dict[str, Any]:
#     """
#     Detailed readiness check with component status.
#     """
#     checks = {
#         "database": await check_database_connection(db),
#         "cache": await check_cache_connection(),
#     }
#
#     all_healthy = all(
#         check["healthy"] for check in checks.values()
#     )
#
#     return {
#         "status": "ready" if all_healthy else "not_ready",
#         "checks": checks
#     }
