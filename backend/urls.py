from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),  # Adjust if your API urls are elsewhere
]

# Catch-all for React frontend routes (serves index.html for all non-API paths)
urlpatterns += [
    re_path(r"^(?!api/).*", TemplateView.as_view(template_name="index.html")),
]
