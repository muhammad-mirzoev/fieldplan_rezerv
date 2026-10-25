"""
- TextChoices даёт список областей: в БД пишется короткий код (chui), в интерфейсе красивое название. Этот список понадобится для зон (длина сезона, заморозки).
- center_lat/lon главные поля: все API NASA принимают координаты точки.
- boundary нужна для рисования на карте и расчёта площади (12.4 га на скриншоте). Площадь посчитаем на фронте и отправим вместе с границей.
- owner может быть пустым. Войти можно будет позже, а демо работает без регистрации.
"""

from django.conf import settings
from django.db import models


class Region(models.TextChoices):
    CHUI = "chui", "Чуйская область"
    TALAS = "talas", "Таласская область"
    ISSYK_KUL = "issyk_kul", "Иссык-Кульская область"
    NARYN = "naryn", "Нарынская область"
    OSH = "osh", "Ошская область"
    JALAL_ABAD = "jalal_abad", "Джалал-Абадская область"
    BATKEN = "batken", "Баткенская область"


class Field(models.Model):
    """Участок фермера: «Поле №1», «Поле №2» на вкладках."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,          # пока без обязательной авторизации
        related_name="fields",
    )
    name = models.CharField("Название", max_length=100, default="Поле")
    region = models.CharField("Область", max_length=20, choices=Region.choices,
                              default=Region.CHUI)

    # Граница: GeoJSON Polygon, который рисуют на карте
    boundary = models.JSONField("Границы (GeoJSON)", null=True, blank=True)

    # Центр поля: по нему запрашиваем NASA POWER, SoilGrids и т.д.
    center_lat = models.FloatField("Широта")
    center_lon = models.FloatField("Долгота")

    area_ha = models.FloatField("Площадь, га", null=True, blank=True)
    elevation_m = models.IntegerField("Высота, м", null=True, blank=True)  # из SRTM

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Поле"
        verbose_name_plural = "Поля"

    def __str__(self):
        return f"{self.name} ({self.get_region_display()}, {self.area_ha or '?'} га)"