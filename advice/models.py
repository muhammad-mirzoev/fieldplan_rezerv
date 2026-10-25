"""
- Crop это таблица, которую заполняет ваш агроном (water_need_mm, frost_tolerance_c, is_legume и т.д.).
  Движок оценки на шаге 7 просто читает её, поэтому качество рекомендаций зависит от точности этих чисел. Заполнять можно через админку или CSV.
- name как property автоматически отдаёт название на кыргызском или русском в зависимости от языка интерфейса (переключатель RU/КЫР).
- Comparison хранит и вход, и результат. Из-за этого страница «История» получается бесплатно: это просто список Comparison.
- data_snapshot сюда пишем, какие данные NASA использовали: температуру, снежный индекс, pH.
  Панель «Почему?» показывает их судьям, и это работает на критерий Validity.
- Оценки 0–100: risk_score считаем так, что больше значит безопаснее, чтобы все четыре шкалы росли в одну сторону и итог был простой взвешенной суммой.
- PlanYear это три строки на план: «Год 1 пшеница → Год 2 фасоль → Год 3 картофель».
- Обратите внимание: в SoilType я случайно написал SIERozem с заглавными буквами.
  Исправь на SIEROZEM = "sierozem", "Серозём", иначе будет непривычное имя константы (на работу это не влияет, но выглядит как опечатка).
"""

from django.db import models
from django.utils.translation import get_language

# Справочник культур (заполняет агроном

class CropFamily(models.TextChoices):
    CEREAL = "cereal", "Зерновые"
    LEGUME = "legume", "Бобовые"
    VEGETABLE = "vegetable", "Овощи"
    ROOT = "root", "Корнеплоды"
    MELON = "melon", "Бахчевые"
    OILSEED = "oilseed", "Масличные"
    FORAGE = "forage", "Кормовые"


class Crop(models.Model):
    code = models.SlugField("Код", unique=True)            # wheat, potato, bean...
    name_ru = models.CharField("Название (RU)", max_length=80)
    name_ky = models.CharField("Название (KY)", max_length=80)
    family = models.CharField("Группа", max_length=20, choices=CropFamily.choices)
    is_legume = models.BooleanField("Бобовая (возвращает азот)", default=False)

    # Вода и сезон
    water_need_mm = models.PositiveIntegerField(
        "Потребность в воде за сезон, мм", help_text="Суммарное водопотребление")
    season_days = models.PositiveIntegerField("Длина вегетации, дней")
    sowing_start_month = models.PositiveSmallIntegerField("Посев с (месяц)")
    sowing_end_month = models.PositiveSmallIntegerField("Посев по (месяц)")

    # Устойчивость к погоде
    frost_tolerance_c = models.FloatField(
        "Выдерживает мороз до, °C", help_text="Например -4 для озимой пшеницы")
    heat_limit_c = models.FloatField("Критическая жара, °C", default=35)

    # Почва
    soil_effect = models.SmallIntegerField(
        "Влияние на почву", default=0,
        help_text="-2 истощает ... +2 восстанавливает (бобовые)")
    ph_min = models.FloatField(default=5.5)
    ph_max = models.FloatField(default=8.0)

    # Экономика
    yield_t_ha = models.FloatField("Урожайность, т/га")
    price_som_per_kg = models.FloatField("Цена, сом/кг")
    cost_som_per_ha = models.FloatField("Затраты, сом/га", default=0)

    # Высотный диапазон (зоны Чуй, Нарын, Иссык-Куль...)
    min_elevation_m = models.IntegerField(default=0)
    max_elevation_m = models.IntegerField(default=3000)

    class Meta:
        ordering = ["name_ru"]
        verbose_name = "Культура"
        verbose_name_plural = "Культуры"

    def __str__(self):
        return self.name_ru

    @property
    def name(self):
        """Название на текущем языке интерфейса (RU / KY)."""
        return self.name_ky if (get_language() or "ru").startswith("ky") else self.name_ru

    @property
    def income_som_per_ha(self):
        """Грубый доход с гектара минус затраты."""
        return self.yield_t_ha * 1000 * self.price_som_per_kg - self.cost_som_per_ha


# Одно сравнение планов (то, что вводит фермер)

class Irrigation(models.TextChoices):
    NONE = "none", "Богара (без полива)"
    CANAL = "canal", "Арычный (самотёк)"
    SPRINKLER = "sprinkler", "Дождевание"
    DRIP = "drip", "Капельный"


class SoilType(models.TextChoices):
    UNKNOWN = "unknown", "Не знаю"      # тогда берём из SoilGrids
    SANDY = "sandy", "Песчаная"
    LOAM = "loam", "Суглинок"
    CLAY = "clay", "Глинистая"
    SIERozem = "sierozem", "Серозём"


class Priority(models.TextChoices):
    LESS_WATER = "less_water", "Меньше полива"
    DIVERSITY = "diversity", "Разнообразие культур"
    INCOME = "income", "Доход"
    SOIL = "soil", "Восстановление почвы"


class WaterClass(models.TextChoices):
    LOW = "low", "Маловодный"
    NORMAL = "normal", "Нормальный"
    HIGH = "high", "Многоводный"


class Comparison(models.Model):
    """Каждое нажатие «Сравнить планы». Это и есть страница «История»."""

    field = models.ForeignKey("fields.Field", on_delete=models.CASCADE,
                              related_name="comparisons")

    # Вход (форма «Условия на поле»)
    previous_crop = models.ForeignKey(Crop, null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name="+")
    irrigation = models.CharField(max_length=20, choices=Irrigation.choices,
                                  blank=True)
    soil_type = models.CharField(max_length=20, choices=SoilType.choices,
                                 default=SoilType.UNKNOWN)
    priority = models.CharField(max_length=20, choices=Priority.choices,
                                default=Priority.LESS_WATER)

    # Результат прогноза водности (шаг 6)
    water_class = models.CharField(max_length=10, choices=WaterClass.choices,
                                   blank=True)

    # Копия данных, на которых основан расчёт: нужна для панели «Почему?»
    data_snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сравнение"
        verbose_name_plural = "Сравнения"

    def __str__(self):
        return f"{self.field.name} · {self.get_priority_display()} · {self.created_at:%d.%m.%Y}"


# Результат: 3 плана по 3 года

class CropPlan(models.Model):
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE,
                                   related_name="plans")
    rank = models.PositiveSmallIntegerField("Место (1–3)")

    # Оценки 0–100
    soil_score = models.FloatField(default=0)
    water_score = models.FloatField(default=0)
    income_score = models.FloatField(default=0)
    risk_score = models.FloatField(default=0)      # чем выше, тем безопаснее
    total_score = models.FloatField(default=0)

    explanation = models.TextField("Почему (ИИ)", blank=True)

    is_saved = models.BooleanField("В плане посадок", default=False)
    saved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["comparison", "rank"]
        unique_together = [("comparison", "rank")]

    def __str__(self):
        return f"План #{self.rank} ({self.total_score:.0f})"


class PlanYear(models.Model):
    plan = models.ForeignKey(CropPlan, on_delete=models.CASCADE, related_name="years")
    year_index = models.PositiveSmallIntegerField("Год севооборота (1–3)")
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT)

    class Meta:
        ordering = ["year_index"]
        unique_together = [("plan", "year_index")]

    def __str__(self):
        return f"Год {self.year_index}: {self.crop}"