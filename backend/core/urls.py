"""
URL configuration for core project.

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

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from api.views import (
    health_check,
    get_characters,
    get_weapons,
    get_filter_options,
    filter_characters,
    upload_video,
    stream_video,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health_check"),
    path("api/characters/", get_characters, name="get_characters"),
    path("api/weapons/", get_weapons, name="get_weapons"),
    path("api/filter-options/", get_filter_options, name="get_filter_options"),
    path("api/characters/filter/", filter_characters, name="filter_characters"),
    path("api/videos/upload/", upload_video, name="upload_video"),
    path("media/videos/<str:filename>", stream_video, name="stream_video"),
]

# 开发环境下提供媒体文件服务（使用自定义 Range 支持视图）
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
