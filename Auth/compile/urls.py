from django.urls import path
from compile.views import submit

urlpatterns = [
    path("", submit, name="submit"),
]