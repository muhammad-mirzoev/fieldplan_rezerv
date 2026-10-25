from django.contrib import admin
from .models import Field


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "area_ha", "center_lat", "center_lon", "owner")
    list_filter = ("region",)