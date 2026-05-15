from django.urls import path
from .views import (
    dashboard_territorial,
    index,
    person_create,
    person_delete,
    person_list,
    person_report,
    person_update,
)

urlpatterns = [
    path("", index, name="index"),
    path("list/", person_list, name="person_list"),
    path("relatorio/", person_report, name="person_report"),
    path("mapa/", dashboard_territorial, name="dashboard_territorial"),
    path("new/", person_create, name="person_create"),
    path("edit/<int:pk>/", person_update, name="person_update"),
    path("delete/<int:pk>/", person_delete, name="person_delete"),
]
