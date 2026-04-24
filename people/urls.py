from django.urls import path
from .views import person_create, person_list, person_report, person_update, person_delete

urlpatterns = [
    path("", person_list, name="person_list"),
    path("relatorio/", person_report, name="person_report"),
    path("new/", person_create, name="person_create"),
    path("edit/<int:pk>/", person_update, name="person_update"),
    path("delete/<int:pk>/", person_delete, name="person_delete"),
]
