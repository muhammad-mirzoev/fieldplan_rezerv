import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from advice.models import Crop, Irrigation, Priority, SoilType
from .geo import guess_region
from .models import Field

PRIORITIES = [
    (Priority.LESS_WATER.value, Priority.LESS_WATER.label, "droplet"),
    (Priority.DIVERSITY.value, Priority.DIVERSITY.label, "shuffle"),
]


def _valid_coords(lat, lon):
    return -90 <= lat <= 90 and -180 <= lon <= 180


def my_fields(request, pk=None):
    fields = list(Field.objects.all())
    current = get_object_or_404(Field, pk=pk) if pk else (fields[0] if fields else None)

    latest = None
    if current:
        latest = current.comparisons.prefetch_related("plans__years__crop").first()

    return render(request, "fields/my_fields.html", {
        "fields": fields,
        "current": current,
        "latest": latest,
        "crops": Crop.objects.all(),
        "irrigation_choices": Irrigation.choices,
        "soil_choices": SoilType.choices,
        "priorities": PRIORITIES,
    })


@require_POST
def create_field(request):
    """Кнопка «+ Новый участок»: создаёт пустое поле, границы нарисуют на карте."""
    try:
        lat, lon = float(request.POST["lat"]), float(request.POST["lon"])
        if not _valid_coords(lat, lon):
            raise ValueError
    except (KeyError, ValueError):
        lat, lon = 42.87, 74.59  # Бишкек по умолчанию

    field = Field.objects.create(
        name=f"Поле №{Field.objects.count() + 1}",
        region=guess_region(lat, lon),
        center_lat=lat,
        center_lon=lon,
    )
    return redirect("field_detail", pk=field.pk)


@require_POST
def save_boundary(request, pk):
    """Принимает границу от карты (JSON) и сохраняет её в поле."""
    field = get_object_or_404(Field, pk=pk)
    try:
        data = json.loads(request.body)
        geometry = data["geometry"]
        lat, lon = float(data["lat"]), float(data["lon"])
        area_ha = round(float(data["area_ha"]), 1)
        if geometry.get("type") != "Polygon" or not _valid_coords(lat, lon):
            raise ValueError
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "bad data"}, status=400)

    field.boundary = geometry
    field.center_lat, field.center_lon = lat, lon
    field.area_ha = area_ha
    field.region = guess_region(lat, lon)
    field.save()
    return JsonResponse({"ok": True, "area_ha": field.area_ha,
                         "region": field.get_region_display()})