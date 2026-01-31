"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # Importing include to reference other URL configurations
# Importing the necessary modules for URL routing
from django.conf import settings    # Import settings for static files and other configurations
from django.conf.urls.static import static  # For serving static and media files during development

from django.http import HttpResponse  # Importing HttpResponse for handling requests

from api.health import health_check, readiness_check, detailed_health

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Setting up Swagger documentation for the API
schema_view = get_schema_view(
    openapi.Info(
        title="DSN LMS Backend APIs",
        default_version='v1',
        description="""
## DSN Learning Management System API

This API provides endpoints for:

### Authentication
- User registration and login (JWT-based)
- Password reset via email/OTP
- Token refresh

### Courses
- Browse and search courses
- Course details with sections and lessons
- Reviews and ratings

### Student Features
- Enrollment management
- Progress tracking
- Wishlist
- Q&A

### Instructor Features
- Course creation and management
- Student analytics
- Earnings tracking
- Coupon management

### E-commerce
- Shopping cart
- Checkout with Stripe/PayPal
- Order history

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

Obtain tokens via `/api/v1/user/token/` endpoint.
        """,
        terms_of_service="https://www.dsnresearch.com/terms/",
        contact=openapi.Contact(email="support@dsnresearch.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def home_view(request):
    return HttpResponse("Welcome to Django Backend!")

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Admin URL for the Django admin interface
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    # Health check endpoints for load balancers and monitoring
    path('health/', health_check, name='health-check'),
    path('health/ready/', readiness_check, name='health-ready'),
    path('health/detailed/', detailed_health, name='health-detailed'),

    # Including the API URLs from the api app
    path("api/v1/", include("api.urls")),  # Auth endpoints
    path("api/v1/", include("core.urls")),  # Core LMS endpoints (courses, cart, orders, etc.)
]

# Adding static and media file serving to the URL patterns
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)        



