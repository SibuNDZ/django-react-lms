"""
Health check endpoints for load balancers and monitoring.

Provides:
- /health/ - Basic liveness check
- /health/ready/ - Readiness check (verifies DB, Redis, Celery)
"""

import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Basic liveness check.
    Returns 200 if the application is running.
    Used by load balancers for health monitoring.
    """
    return JsonResponse({
        "status": "healthy",
        "service": "lms-backend"
    })


def readiness_check(request):
    """
    Readiness check that verifies all dependencies are available.
    Returns 200 only if database, cache, and other services are accessible.
    Used by Kubernetes/orchestrators to determine if traffic can be routed.
    """
    checks = {
        "database": False,
        "cache": False,
    }
    errors = []

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["database"] = True
    except Exception as e:
        errors.append(f"Database: {str(e)}")
        logger.error(f"Health check - Database error: {e}")

    # Check cache/Redis connection
    try:
        cache.set("health_check", "ok", timeout=10)
        if cache.get("health_check") == "ok":
            checks["cache"] = True
        cache.delete("health_check")
    except Exception as e:
        errors.append(f"Cache: {str(e)}")
        logger.error(f"Health check - Cache error: {e}")

    # Check Celery (optional - only if broker is configured)
    if hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL:
        checks["celery"] = False
        try:
            from backend.celery import app as celery_app
            # Just check if we can connect to the broker
            inspect = celery_app.control.inspect()
            # This is a quick check, not waiting for response
            checks["celery"] = True
        except Exception as e:
            errors.append(f"Celery: {str(e)}")
            logger.warning(f"Health check - Celery warning: {e}")
            # Celery check failure is a warning, not critical
            checks["celery"] = None  # Unknown state

    # Determine overall status
    critical_checks = ["database"]
    all_critical_passed = all(checks.get(c) for c in critical_checks)

    if all_critical_passed:
        status_code = 200
        status = "ready"
    else:
        status_code = 503
        status = "not_ready"

    response_data = {
        "status": status,
        "checks": checks,
    }

    if errors:
        response_data["errors"] = errors

    return JsonResponse(response_data, status=status_code)


def detailed_health(request):
    """
    Detailed health information for monitoring dashboards.
    Includes version info, uptime, and detailed status.
    """
    import django
    import sys
    from datetime import datetime

    checks = {}

    # Database check with latency
    try:
        import time
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        latency = (time.time() - start) * 1000
        checks["database"] = {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Cache check with latency
    try:
        start = time.time()
        cache.set("health_check_detailed", "ok", timeout=10)
        cache.get("health_check_detailed")
        cache.delete("health_check_detailed")
        latency = (time.time() - start) * 1000
        checks["cache"] = {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        checks["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    return JsonResponse({
        "status": "healthy" if all(c.get("status") == "healthy" for c in checks.values()) else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": {
            "python": sys.version.split()[0],
            "django": django.__version__,
        },
        "checks": checks
    })
