"""
i18n/ даёт готовый адрес set_language: он принимает язык и запоминает его в сессии. Своего кода для переключения писать не нужно.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # переключатель языка
    path("", include("fields.urls")),
    path("", include("advice.urls")),
]