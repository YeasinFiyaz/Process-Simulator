# procsim/sim/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/simulate", views.api_simulate, name="api_simulate"),
]
