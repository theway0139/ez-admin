"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ops.api import api as ops_api
from api.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api2/', ops_api.urls),
    path('api/', api.urls),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
