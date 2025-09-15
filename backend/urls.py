from django.contrib import admin
from django.urls import path, re_path, include
from api.Views.FrontendAppView import FrontendAppView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

# Catch-all for React frontend routes (serves index.html for all non-API paths)
urlpatterns += [
    re_path(r"^(?!api/).*", FrontendAppView.as_view()),
]
