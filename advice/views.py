from django.shortcuts import get_object_or_404, redirect, render

from fields.models import Field
from .forms import ComparisonForm
from .models import CropPlan, Comparison


def compare(request, field_id):
    """Кнопка «Сравнить планы». Пока только сохраняет условия.
    Настоящий расчёт подключим на шаге 7."""
    field = get_object_or_404(Field, pk=field_id)
    if request.method == "POST":
        form = ComparisonForm(request.POST)
        if form.is_valid():
            comparison = form.save(commit=False)
            comparison.field = field
            comparison.save()
            # TODO шаг 7: здесь вызовем движок оценки и создадим 3 CropPlan
    return redirect("field_detail", pk=field.pk)


def plans(request):
    saved = (CropPlan.objects.filter(is_saved=True)
             .select_related("comparison__field")
             .prefetch_related("years__crop"))
    return render(request, "advice/plans.html", {"plans": saved})


def history(request):
    items = (Comparison.objects.select_related("field", "previous_crop")
             .prefetch_related("plans"))
    return render(request, "advice/history.html", {"items": items})


def help_page(request):
    return render(request, "advice/help.html")