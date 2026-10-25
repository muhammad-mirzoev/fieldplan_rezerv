from django.contrib import admin
from .models import Crop, Comparison, CropPlan, PlanYear


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_ky", "family", "is_legume",
                    "water_need_mm", "season_days", "frost_tolerance_c")
    list_filter = ("family", "is_legume")
    search_fields = ("name_ru", "name_ky", "code")
    prepopulated_fields = {"code": ("name_ru",)}


class PlanYearInline(admin.TabularInline):
    model = PlanYear
    extra = 0


@admin.register(CropPlan)
class CropPlanAdmin(admin.ModelAdmin):
    list_display = ("comparison", "rank", "total_score", "is_saved")
    inlines = [PlanYearInline]


admin.site.register(Comparison)