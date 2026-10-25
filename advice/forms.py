from django import forms
from .models import Comparison


class ComparisonForm(forms.ModelForm):
    """Форма «Условия на поле». Django сам проверяет, что значения допустимы."""

    class Meta:
        model = Comparison
        fields = ["previous_crop", "irrigation", "soil_type", "priority"]