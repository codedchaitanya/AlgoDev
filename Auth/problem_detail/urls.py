from django.urls import path
from problem_detail.views import Detail

urlpatterns = [
    path("detail/", Detail, name="detail"),
    
]