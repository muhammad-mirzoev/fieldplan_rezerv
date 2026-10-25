"""
Перед каждым запросом к NASA клиент сначала смотрит в эту таблицу.
Координаты будем округлять до 2 знаков (около 1 км), чтобы близкие поля использовали один кэш.
Это также защита от падения сети на самом хакатоне.
"""

from django.db import models


class DatasetCache(models.Model):
    """Кэш ответов NASA / SoilGrids, чтобы демо не зависело от их серверов."""

    dataset = models.CharField(max_length=40)       # power, modis_snow, soilgrids
    lat = models.FloatField()
    lon = models.FloatField()
    params = models.CharField(max_length=200, blank=True)  # годы, период и т.д.
    payload = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("dataset", "lat", "lon", "params")]
        indexes = [models.Index(fields=["dataset", "lat", "lon"])]

    def __str__(self):
        return f"{self.dataset} @ {self.lat:.2f},{self.lon:.2f}"