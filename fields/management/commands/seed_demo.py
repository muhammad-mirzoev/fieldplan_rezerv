from django.core.management.base import BaseCommand
from fields.models import Field


class Command(BaseCommand):
    help = "Создаёт демо-поля около Сокулука (Чуйская область)"

    def handle(self, *args, **options):
        demo = [
            dict(name="Поле №1", region="chui", center_lat=42.8615,
                 center_lon=74.2990, area_ha=12.4, elevation_m=760),
            dict(name="Поле №2", region="chui", center_lat=42.8420,
                 center_lon=74.3350, area_ha=8.1, elevation_m=775),
        ]
        for item in demo:
            obj, created = Field.objects.get_or_create(name=item["name"], defaults=item)
            self.stdout.write(("создано: " if created else "уже есть: ") + str(obj))