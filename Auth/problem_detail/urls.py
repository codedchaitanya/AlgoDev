from django.urls import path
from . import views


urlpatterns = [
    # path('', views.submit, name='submit'),
    path('submit/',views.submit,name='submit_question'),
    

]   
