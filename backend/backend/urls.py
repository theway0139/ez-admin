"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from ops.api import api as ops_api
from api.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api2/', ops_api.urls),
    path('api/', api.urls),
]
