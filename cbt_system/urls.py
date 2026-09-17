from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Homepage + accounts (login, student-login, teacher-login, etc.)
    path("", include("accounts.urls")),

    # Django Admin
    path("admin/", admin.site.urls),

    # Other apps
    path("exams/", include("exams.urls")),
    path("attempts/", include("attempts.urls")),
]