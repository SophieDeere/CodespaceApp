from django.db import models


class Vegetable(models.Model):
    """Gemüsesorte mit allen Anbau- und Standortinformationen."""

    class Sunlight(models.TextChoices):
        FULL_SUN = "full_sun", "Vollsonne"
        PARTIAL_SHADE = "partial_shade", "Halbschatten"
        SHADE = "shade", "Schatten"

    class WaterRequirement(models.TextChoices):
        LOW = "low", "Gering"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    class NutrientDemand(models.TextChoices):
        LOW = "low", "Schwachzehrer"
        MEDIUM = "medium", "Mittelzehrer"
        HIGH = "high", "Starkzehrer"

    class Category(models.TextChoices):
        FRUIT = "fruit", "Fruchtgemüse"
        LEAF = "leaf", "Blattgemüse"
        ROOT = "root", "Wurzelgemüse"
        BULB = "bulb", "Zwiebelgemüse"
        LEGUME = "legume", "Hülsenfrüchte"
        BRASSICA = "brassica", "Kohlgemüse"
        HERB = "herb", "Kräuter"
        OTHER = "other", "Sonstiges"

    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name="Kategorie",
    )
    description = models.TextField(blank=True, verbose_name="Beschreibung")

    # Standortansprüche
    sunlight_requirement = models.CharField(
        max_length=20,
        choices=Sunlight.choices,
        default=Sunlight.FULL_SUN,
        verbose_name="Lichtbedarf",
    )
    water_requirement = models.CharField(
        max_length=10,
        choices=WaterRequirement.choices,
        default=WaterRequirement.MEDIUM,
        verbose_name="Wasserbedarf",
    )
    soil_type = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Bodentyp",
        help_text="z. B. humusreich, durchlässig, lehmig",
    )
    nutrient_demand = models.CharField(
        max_length=10,
        choices=NutrientDemand.choices,
        default=NutrientDemand.MEDIUM,
        verbose_name="Nährstoffbedarf",
    )

    # Freiland-Zeitfenster (Monat 1–12, None = nicht anwendbar)
    indoor_start_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Voranzucht ab (Monat)"
    )
    indoor_start_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Voranzucht bis (Monat)"
    )
    sow_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Aussaat ab (Monat)"
    )
    sow_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Aussaat bis (Monat)"
    )
    plant_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Pflanzung ab (Monat)"
    )
    plant_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Pflanzung bis (Monat)"
    )
    harvest_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Ernte ab (Monat)"
    )
    harvest_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Ernte bis (Monat)"
    )

    # Gewächshaus-Zeitfenster
    gh_sow_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Aussaat ab (Monat)"
    )
    gh_sow_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Aussaat bis (Monat)"
    )
    gh_plant_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Pflanzung ab (Monat)"
    )
    gh_plant_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Pflanzung bis (Monat)"
    )
    gh_harvest_from = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Ernte ab (Monat)"
    )
    gh_harvest_to = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="GH Ernte bis (Monat)"
    )

    # Saatgut
    saatgut_url = models.URLField(
        blank=True, verbose_name="Saatgut-Link", help_text="z. B. Bingenheimer Saatgut"
    )

    class Meta:
        verbose_name = "Gemüsesorte"
        verbose_name_plural = "Gemüsesorten"
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Bed(models.Model):
    """Gartenbeet mit Standort- und Typangabe."""

    class Location(models.TextChoices):
        FULL_SUN = "full_sun", "Vollsonne"
        PARTIAL_SHADE = "partial_shade", "Halbschatten"
        SHADE = "shade", "Schatten"

    class BedType(models.TextChoices):
        OUTDOOR = "outdoor", "Freiland"
        GREENHOUSE = "greenhouse", "Gewächshaus"

    name = models.CharField(max_length=100, verbose_name="Name")
    size_sqm = models.FloatField(null=True, blank=True, verbose_name="Größe (m²)")
    location = models.CharField(
        max_length=20,
        choices=Location.choices,
        default=Location.FULL_SUN,
        verbose_name="Lage",
    )
    bed_type = models.CharField(
        max_length=20,
        choices=BedType.choices,
        default=BedType.OUTDOOR,
        verbose_name="Typ",
    )
    notes = models.TextField(blank=True, verbose_name="Notizen")

    class Meta:
        verbose_name = "Gartenbeet"
        verbose_name_plural = "Gartenbeete"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_bed_type_display()})"


class BedPlanting(models.Model):
    """Belegung eines Beets mit einer Gemüsesorte in einem Jahr."""

    bed = models.ForeignKey(
        Bed, on_delete=models.CASCADE, related_name="plantings", verbose_name="Beet"
    )
    vegetable = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="plantings",
        verbose_name="Gemüsesorte",
    )
    year = models.PositiveSmallIntegerField(verbose_name="Jahr")
    planted_date = models.DateField(null=True, blank=True, verbose_name="Pflanzdatum")
    notes = models.TextField(blank=True, verbose_name="Notizen")

    class Meta:
        verbose_name = "Beetbelegung"
        verbose_name_plural = "Beetbelegungen"
        ordering = ["-year", "bed", "vegetable"]
        unique_together = [["bed", "vegetable", "year"]]

    def __str__(self):
        return f"{self.vegetable} in {self.bed} ({self.year})"


class NeighborRelation(models.Model):
    """Gute oder schlechte Nachbarschaft zwischen zwei Gemüsesorten."""

    class RelationType(models.TextChoices):
        GOOD = "good", "Guter Nachbar"
        BAD = "bad", "Schlechter Nachbar"

    vegetable = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="neighbor_relations",
        verbose_name="Gemüsesorte",
    )
    neighbor = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="neighbor_of",
        verbose_name="Nachbar",
    )
    relation_type = models.CharField(
        max_length=10, choices=RelationType.choices, verbose_name="Beziehungstyp"
    )
    note = models.TextField(blank=True, verbose_name="Begründung")

    class Meta:
        verbose_name = "Nachbarschaftsbeziehung"
        verbose_name_plural = "Nachbarschaftsbeziehungen"
        unique_together = [["vegetable", "neighbor"]]

    def __str__(self):
        return f"{self.vegetable} ↔ {self.neighbor} ({self.get_relation_type_display()})"


class HerbTip(models.Model):
    """Empfehlung für begleitende Kräuter neben einer Gemüsesorte."""

    vegetable = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="herb_tips",
        verbose_name="Gemüsesorte",
    )
    herb_name = models.CharField(max_length=100, verbose_name="Kräutername")
    benefit = models.TextField(verbose_name="Nutzen")

    class Meta:
        verbose_name = "Kräuter-Tipp"
        verbose_name_plural = "Kräuter-Tipps"

    def __str__(self):
        return f"{self.herb_name} neben {self.vegetable}"


class SuccessionNote(models.Model):
    """Fruchtfolge-Hinweis: Sorte sollte nicht nach avoid_after folgen."""

    vegetable = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="succession_notes",
        verbose_name="Gemüsesorte",
    )
    avoid_after = models.ForeignKey(
        Vegetable,
        on_delete=models.CASCADE,
        related_name="avoid_before",
        verbose_name="Nicht nach dieser Sorte",
    )
    note = models.TextField(blank=True, verbose_name="Begründung")

    class Meta:
        verbose_name = "Fruchtfolge-Hinweis"
        verbose_name_plural = "Fruchtfolge-Hinweise"
        unique_together = [["vegetable", "avoid_after"]]

    def __str__(self):
        return f"{self.vegetable} nicht nach {self.avoid_after}"


class WateringReminder(models.Model):
    """Gießerinnerung für ein Beet, optional wetterabhängig."""

    bed = models.OneToOneField(
        Bed,
        on_delete=models.CASCADE,
        related_name="watering_reminder",
        verbose_name="Beet",
    )
    interval_days = models.PositiveSmallIntegerField(
        default=2, verbose_name="Intervall (Tage)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    last_watered = models.DateField(null=True, blank=True, verbose_name="Zuletzt gegossen")
    next_watering = models.DateField(null=True, blank=True, verbose_name="Nächstes Gießen")
    weather_suppressed = models.BooleanField(
        default=False,
        verbose_name="Wetter-unterdrückt",
        help_text="Wird in Iteration 3 durch Wetterlogik gesetzt",
    )

    class Meta:
        verbose_name = "Gießerinnerung"
        verbose_name_plural = "Gießerinnerungen"

    def __str__(self):
        return f"Gießerinnerung für {self.bed} (alle {self.interval_days} Tage)"


class FertilizingReminder(models.Model):
    """Düngeerinnerung für eine Beetbelegung (sortenspezifisch)."""

    bed_planting = models.OneToOneField(
        BedPlanting,
        on_delete=models.CASCADE,
        related_name="fertilizing_reminder",
        verbose_name="Beetbelegung",
    )
    interval_days = models.PositiveSmallIntegerField(
        default=30, verbose_name="Intervall (Tage)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    last_fertilized = models.DateField(null=True, blank=True, verbose_name="Zuletzt gedüngt")
    next_fertilizing = models.DateField(null=True, blank=True, verbose_name="Nächstes Düngen")

    class Meta:
        verbose_name = "Düngeerinnerung"
        verbose_name_plural = "Düngeerinnerungen"

    def __str__(self):
        return f"Düngeerinnerung für {self.bed_planting}"