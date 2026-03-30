from django.urls import path
from .views import person_create, person_list

urlpatterns = [
    path("", person_list, name="person_list"),
    path("new/", person_create, name="person_create"),
]