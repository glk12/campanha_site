from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PersonForm
from .models import Person


def home_page(request):
    return render(request, "people/home.html")

def index(request):
    return render(request, "people/index.html")

def person_list(request):
    people = Person.objects.all()
    return render(request, "people/person_list.html", {"people": people})


def person_report(request):
    responsible_filter = request.GET.get("responsavel", "")

    people = Person.objects.select_related("parent").all().order_by("full_name")

    total_people = Person.objects.count()
    total_without_responsible = Person.objects.filter(parent__isnull=True).count()
    responsible_options = (
        Person.objects.annotate(total_records=Count("children"))
        .filter(total_records__gt=0)
        .order_by("full_name")
    )

    current_filter_label = "Todos"

    if responsible_filter == "none":
        people = people.filter(parent__isnull=True)
        current_filter_label = "Sem responsável"
    elif responsible_filter.isdigit():
        selected_responsible = Person.objects.filter(pk=responsible_filter).first()
        if selected_responsible:
            people = people.filter(parent=selected_responsible)
            current_filter_label = selected_responsible.full_name

    filtered_total = people.count()

    return render(
        request,
        "people/person_report.html",
        {
            "people": people,
            "total_people": total_people,
            "filtered_total": filtered_total,
            "total_without_responsible": total_without_responsible,
            "responsible_options": responsible_options,
            "responsible_filter": responsible_filter,
            "current_filter_label": current_filter_label,
        },
    )


def person_create(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("person_list")
    else:
        form = PersonForm()

    return render(request, "people/person_form.html", {"form": form})


def person_update(request, pk):
    person = get_object_or_404(Person, pk=pk)

    if request.method == "POST":
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect("person_list")
    else:
        form = PersonForm(instance=person)

    return render(
        request,
        "people/person_form.html",
        {"form": form, "person": person, "is_edit": True},
    )


def person_delete(request, pk):
    person = get_object_or_404(Person, pk=pk)

    if request.method == "POST":
        person.delete()
        return redirect("person_list")

    return render(request, "people/person_confirm_delete.html", {"person": person})
