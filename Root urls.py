# procsim/procsim/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sim.urls")),  # route everything to the sim app
]
