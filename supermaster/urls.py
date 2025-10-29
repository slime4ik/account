from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('account.urls')),
    # Simple JWT
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
    )

    urlpatterns += [
        # Свагер
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        # Simple JWT
        path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        # Silk
        path('silk/', include('silk.urls', namespace='silk'))
    ]