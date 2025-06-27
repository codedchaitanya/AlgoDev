from django.shortcuts import render
from .models import Detail

def prob_description():
    details = Detail.objects.all()

    return render(request, "question_detail.html", details:details)
    