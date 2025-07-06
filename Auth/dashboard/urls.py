from django.urls import path
from dashboard.views import dashboard,problem_detail,leaderboard_view
from . import views

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("problem/<int:id>", problem_detail, name="problem_detail"),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]