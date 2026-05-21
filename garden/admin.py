from django.contrib import admin

from .models import (
    Bed,
    BedPlanting,
    FertilizingReminder,
    HerbTip,
    NeighborRelation,
    SuccessionNote,
    Vegetable,
    WateringReminder,
)


class NeighborRelationInline(admin.TabularInline):
    model = NeighborRelation
    fk_name = "vegetable"
    extra = 1
    verbose_name = "Nachbarschaftsbeziehung"
    verbose_name_plural = "Nachbarschaftsbeziehungen"
    autocomplete_fields = ["neighbor"]


class HerbTipInline(admin.TabularInline):
    model = HerbTip
    extra = 1
    verbose_name = "Kräuter-Tipp"
    verbose_name_plural = "Kräuter-Tipps"


class SuccessionNoteInline(admin.TabularInline):
    model = SuccessionNote
    fk_name = "vegetable"
    extra = 1
    verbose_name = "Fruchtfolge-Hinweis"
    verbose_name_plural = "Fruchtfolge-Hinweise"
    autocomplete_fields = ["avoid_after"]


class BedPlantingInline(admin.TabularInline):
    model = BedPlanting
    extra = 1
    verbose_name = "Beetbelegung"
    verbose_name_plural = "Beetbelegungen"
    autocomplete_fields = ["vegetable"]


class WateringReminderInline(admin.StackedInline):
    model = WateringReminder
    extra = 0
    verbose_name = "Gießerinnerung"
    can_delete = False


class FertilizingReminderInline(admin.StackedInline):
    model = FertilizingReminder
    extra = 0
    verbose_name = "Düngeerinnerung"
    can_delete = False


@admin.register(Vegetable)
class VegetableAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "sunlight_requirement",
        "water_requirement", "nutrient_demand",
        "sow_from", "sow_to", "harvest_from", "harvest_to",
    ]
    list_filter = ["category", "sunlight_requirement", "nutrient_demand"]
    search_fields = ["name"]
    ordering = ["category", "name"]
    fieldsets = [
        ("Allgemein", {"fields": ["name", "category", "description"]}),
        ("Standortansprüche", {"fields": [
            "sunlight_requirement", "water_requirement",
            "soil_type", "nutrient_demand",
        ]}),
        ("Freiland – Zeitfenster (Monat 1–12)", {"fields": [
            ("indoor_start_from", "indoor_start_to"),
            ("sow_from", "sow_to"),
            ("plant_from", "plant_to"),
            ("harvest_from", "harvest_to"),
        ]}),
        ("Gewächshaus – Zeitfenster (Monat 1–12)", {"classes": ["collapse"], "fields": [
            ("gh_sow_from", "gh_sow_to"),
            ("gh_plant_from", "gh_plant_to"),
            ("gh_harvest_from", "gh_harvest_to"),
        ]}),
        ("Saatgut", {"fields": ["saatgut_url"]}),
    ]
    inlines = [NeighborRelationInline, HerbTipInline, SuccessionNoteInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ["name", "bed_type", "location", "size_sqm"]
    list_filter = ["bed_type", "location"]
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [BedPlantingInline, WateringReminderInline]


@admin.register(BedPlanting)
class BedPlantingAdmin(admin.ModelAdmin):
    list_display = ["vegetable", "bed", "year", "planted_date"]
    list_filter = ["year", "bed"]
    search_fields = ["vegetable__name", "bed__name"]
    autocomplete_fields = ["bed", "vegetable"]
    ordering = ["-year", "bed", "vegetable"]
    inlines = [FertilizingReminderInline]


@admin.register(WateringReminder)
class WateringReminderAdmin(admin.ModelAdmin):
    list_display = [
        "bed", "interval_days", "is_active",
        "last_watered", "next_watering", "weather_suppressed",
    ]
    list_filter = ["is_active", "weather_suppressed"]
    autocomplete_fields = ["bed"]


@admin.register(FertilizingReminder)
class FertilizingReminderAdmin(admin.ModelAdmin):
    list_display = [
        "bed_planting", "interval_days", "is_active",
        "last_fertilized", "next_fertilizing",
    ]
    list_filter = ["is_active"]