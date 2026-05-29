from datetime import date, timedelta

from django.shortcuts import get_object_or_404, redirect, render

from .models import Bed, BedPlanting, FertilizingReminder, Vegetable, WateringReminder


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def dashboard(request):
    beds = Bed.objects.prefetch_related("plantings__vegetable").all()
    return render(request, "garden/dashboard.html", {"beds": beds})


# ---------------------------------------------------------------------------
# Beete
# ---------------------------------------------------------------------------

def bed_list(request):
    beds = Bed.objects.prefetch_related("plantings__vegetable").all()
    return render(request, "garden/bed_list.html", {"beds": beds})


def bed_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        size_sqm = request.POST.get("size_sqm") or None
        location = request.POST.get("location")
        bed_type = request.POST.get("bed_type")
        notes = request.POST.get("notes", "")
        if name:
            Bed.objects.create(
                name=name,
                size_sqm=size_sqm,
                location=location,
                bed_type=bed_type,
                notes=notes,
            )
            return redirect("bed_list")
    return render(request, "garden/bed_form.html", {
        "title": "Neues Beet anlegen",
        "location_choices": Bed.Location.choices,
        "bed_type_choices": Bed.BedType.choices,
    })


def bed_edit(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == "POST":
        bed.name = request.POST.get("name", "").strip()
        bed.size_sqm = request.POST.get("size_sqm") or None
        bed.location = request.POST.get("location")
        bed.bed_type = request.POST.get("bed_type")
        bed.notes = request.POST.get("notes", "")
        bed.save()
        return redirect("bed_list")
    return render(request, "garden/bed_form.html", {
        "title": "Beet bearbeiten",
        "bed": bed,
        "location_choices": Bed.Location.choices,
        "bed_type_choices": Bed.BedType.choices,
    })


def bed_delete(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == "POST":
        bed.delete()
        return redirect("bed_list")
    return render(request, "garden/bed_confirm_delete.html", {"bed": bed})


def bed_detail(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    plantings = bed.plantings.select_related(
        "vegetable", "fertilizing_reminder"
    ).filter(year=2026)
    vegetables = Vegetable.objects.order_by("category", "name")

    # Gießerinnerung holen oder None
    try:
        watering = bed.watering_reminder
    except WateringReminder.DoesNotExist:
        watering = None

    return render(request, "garden/bed_detail.html", {
        "bed": bed,
        "plantings": plantings,
        "vegetables": vegetables,
        "watering": watering,
        "today": date.today(),
    })


# ---------------------------------------------------------------------------
# Beetbelegung
# ---------------------------------------------------------------------------

def planting_add(request, bed_pk):
    bed = get_object_or_404(Bed, pk=bed_pk)
    if request.method == "POST":
        vegetable_id = request.POST.get("vegetable")
        vegetable = get_object_or_404(Vegetable, pk=vegetable_id)
        BedPlanting.objects.get_or_create(bed=bed, vegetable=vegetable, year=2026)
        return redirect("bed_detail", pk=bed_pk)
    return redirect("bed_detail", pk=bed_pk)


def planting_remove(request, pk):
    planting = get_object_or_404(BedPlanting, pk=pk)
    bed_pk = planting.bed.pk
    if request.method == "POST":
        planting.delete()
    return redirect("bed_detail", pk=bed_pk)


# ---------------------------------------------------------------------------
# Gießerinnerung
# ---------------------------------------------------------------------------

def watering_save(request, bed_pk):
    """Gießerinnerung anlegen oder aktualisieren."""
    bed = get_object_or_404(Bed, pk=bed_pk)
    if request.method == "POST":
        interval_days = int(request.POST.get("interval_days", 2))
        last_watered_str = request.POST.get("last_watered") or None
        last_watered = date.fromisoformat(last_watered_str) if last_watered_str else date.today()
        next_watering = last_watered + timedelta(days=interval_days)

        watering, _ = WateringReminder.objects.get_or_create(bed=bed)
        watering.interval_days = interval_days
        watering.is_active = True
        watering.last_watered = last_watered
        watering.next_watering = next_watering
        watering.save()
    return redirect("bed_detail", pk=bed_pk)


def watering_done(request, bed_pk):
    """Gießen als erledigt markieren – nächsten Termin berechnen."""
    bed = get_object_or_404(Bed, pk=bed_pk)
    if request.method == "POST":
        try:
            watering = bed.watering_reminder
            watering.last_watered = date.today()
            watering.next_watering = date.today() + timedelta(days=watering.interval_days)
            watering.weather_suppressed = False
            watering.save()
        except WateringReminder.DoesNotExist:
            pass
    return redirect("bed_detail", pk=bed_pk)


def watering_delete(request, bed_pk):
    """Gießerinnerung löschen."""
    bed = get_object_or_404(Bed, pk=bed_pk)
    if request.method == "POST":
        try:
            bed.watering_reminder.delete()
        except WateringReminder.DoesNotExist:
            pass
    return redirect("bed_detail", pk=bed_pk)


# ---------------------------------------------------------------------------
# Düngeerinnerung
# ---------------------------------------------------------------------------

def fertilizing_save(request, planting_pk):
    """Düngeerinnerung für eine Beetbelegung anlegen oder aktualisieren."""
    planting = get_object_or_404(BedPlanting, pk=planting_pk)
    if request.method == "POST":
        interval_days = int(request.POST.get("interval_days", 30))
        last_fertilized_str = request.POST.get("last_fertilized") or None
        last_fertilized = date.fromisoformat(last_fertilized_str) if last_fertilized_str else date.today()
        next_fertilizing = last_fertilized + timedelta(days=interval_days)

        reminder, _ = FertilizingReminder.objects.get_or_create(bed_planting=planting)
        reminder.interval_days = interval_days
        reminder.is_active = True
        reminder.last_fertilized = last_fertilized
        reminder.next_fertilizing = next_fertilizing
        reminder.save()
    return redirect("bed_detail", pk=planting.bed.pk)


def fertilizing_done(request, planting_pk):
    """Düngen als erledigt markieren."""
    planting = get_object_or_404(BedPlanting, pk=planting_pk)
    if request.method == "POST":
        try:
            reminder = planting.fertilizing_reminder
            reminder.last_fertilized = date.today()
            reminder.next_fertilizing = date.today() + timedelta(days=reminder.interval_days)
            reminder.save()
        except FertilizingReminder.DoesNotExist:
            pass
    return redirect("bed_detail", pk=planting.bed.pk)


def fertilizing_delete(request, planting_pk):
    """Düngeerinnerung löschen."""
    planting = get_object_or_404(BedPlanting, pk=planting_pk)
    if request.method == "POST":
        try:
            planting.fertilizing_reminder.delete()
        except FertilizingReminder.DoesNotExist:
            pass
    return redirect("bed_detail", pk=planting.bed.pk)


# ---------------------------------------------------------------------------
# Gemüsesorten & Anbaukalender
# ---------------------------------------------------------------------------

def vegetable_list(request):
    category = request.GET.get("category", "")
    vegetables = Vegetable.objects.all()
    if category:
        vegetables = vegetables.filter(category=category)
    vegetables = vegetables.order_by("category", "name")
    return render(request, "garden/vegetable_list.html", {
        "vegetables": vegetables,
        "category_choices": Vegetable.Category.choices,
        "selected_category": category,
    })


def vegetable_detail(request, pk):
    vegetable = get_object_or_404(Vegetable, pk=pk)
    good_neighbors = vegetable.neighbor_relations.filter(
        relation_type="good"
    ).select_related("neighbor")
    bad_neighbors = vegetable.neighbor_relations.filter(
        relation_type="bad"
    ).select_related("neighbor")
    herb_tips = vegetable.herb_tips.all()
    succession_notes = vegetable.succession_notes.select_related("avoid_after")

    return render(request, "garden/vegetable_detail.html", {
        "vegetable": vegetable,
        "good_neighbors": good_neighbors,
        "bad_neighbors": bad_neighbors,
        "herb_tips": herb_tips,
        "succession_notes": succession_notes,
        "months": [
            "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
            "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"
        ],
    })