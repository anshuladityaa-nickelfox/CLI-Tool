from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # Feature URLs will be added here
    path('api/logging_system/', include('apps.logging_system.urls')),
    path('api/error_handler/', include('apps.error_handler.urls')),
    path('api/uploads/', include('apps.uploads.urls')),
    path('api/rbac/', include('apps.rbac.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/mail_service/', include('apps.mail_service.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)