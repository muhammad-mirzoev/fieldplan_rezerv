"""
Адреса /plans и /history (forma-five-henna.vercel.app/plans).
"""

from django.urls import path
from . import views

urlpatterns = [
    path("fields/<int:field_id>/compare/", views.compare, name="compare"),
    path("plans/", views.plans, name="plans"),
    path("history/", views.history, name="history"),
    path("help/", views.help_page, name="help"),
]