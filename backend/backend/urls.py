"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from users.views import send_otp, verify_otp, change_user_role  # RBAC: Add change_user_role

urlpatterns = [
    path('admin/', admin.site.urls),

    # DJOSER auth endpoints including /activation/
    path('api/v1/auth/', include('djoser.urls')),         # handles registration, activation, etc.
    path('api/v1/auth/', include('djoser.urls.jwt')),     # handles JWT create/refresh/logout

    # OTP
    path('api/v1/otp/send/', send_otp, name='send-otp'),
    path('api/v1/otp/verify/', verify_otp, name='verify-otp'),

    # RBAC: Admin-only role change endpoint
    path('api/v1/admin/users/<int:user_id>/role/', change_user_role, name='change-user-role'),
]
