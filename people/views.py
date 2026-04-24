from django.shortcuts import get_object_or_404, redirect, render
from .forms import PersonForm
from .models import Person

def person_list(request):
    people = Person.objects.all()
    return render(request, "people/person_list.html", {"people": people})


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


