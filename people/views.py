from django.shortcuts import render, redirect
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
            return redirect("people/person_list.html")
    else:
        form = PersonForm()

    return render(request, "people/person_form.html", {"form": form})


