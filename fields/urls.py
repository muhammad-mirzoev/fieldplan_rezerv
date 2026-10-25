from django.urls import path
from . import views

urlpatterns = [
    path("", views.my_fields, name="my_fields"),
    path("fields/new/", views.create_field, name="field_create"),
    path("fields/<int:pk>/", views.my_fields, name="field_detail"),
    path("fields/<int:pk>/boundary/", views.save_boundary, name="field_boundary"),
]