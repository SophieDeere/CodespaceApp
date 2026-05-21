from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Beete
    path("beete/", views.bed_list, name="bed_list"),
    path("beete/neu/", views.bed_create, name="bed_create"),
    path("beete/<int:pk>/", views.bed_detail, name="bed_detail"),
    path("beete/<int:pk>/bearbeiten/", views.bed_edit, name="bed_edit"),
    path("beete/<int:pk>/loeschen/", views.bed_delete, name="bed_delete"),

    # Beetbelegung
    path("beete/<int:bed_pk>/belegung/hinzufuegen/", views.planting_add, name="planting_add"),
    path("belegung/<int:pk>/entfernen/", views.planting_remove, name="planting_remove"),

    # Gemüsesorten
    path("gemuese/", views.vegetable_list, name="vegetable_list"),
    path("gemuese/<int:pk>/", views.vegetable_detail, name="vegetable_detail"),
]

