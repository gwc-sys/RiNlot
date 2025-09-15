from django.contrib import admin
from django.urls import path, re_path, include
from api.Views.FrontendAppView import FrontendAppView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    re_path(r"^(?!api/).*", FrontendAppView.as_view()),
]

