from django.shortcuts import get_object_or_404, redirect, render

from .models import Bed, BedPlanting, Vegetable


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
    plantings = bed.plantings.select_related("vegetable").filter(year=2026)
    vegetables = Vegetable.objects.order_by("category", "name")
    return render(request, "garden/bed_detail.html", {
        "bed": bed,
        "plantings": plantings,
        "vegetables": vegetables,
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
    # Nachbarn
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


