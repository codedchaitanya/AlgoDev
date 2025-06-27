from django.shortcuts import render, redirect
from .models import Question, Topic, UserQuestionStatus
from django.contrib.auth.decorators import login_required


def dashboard(request):
    topics = Topic.objects.all()
    selected_topic_id = request.GET.get("topic")

    if selected_topic_id:
        questions = Question.objects.filter(is_active=True, topic_id=selected_topic_id)
    else:
        # Default to "Array" topic (or any topic you want as default)
        default_topic = Topic.objects.filter(name__iexact="array").first()
        questions = Question.objects.filter(is_active=True, topic=default_topic)

    context = {
        "topics": topics,
        "questions": questions,
        "selected_topic_id": int(selected_topic_id) if selected_topic_id else default_topic.id,
    }
    return render(request, "dashboard.html", context)

@login_required
def toggle_favorite(request, question_id):
    status, _ = UserQuestionStatus.objects.get_or_create(user=request.user, question_id=question_id)
    status.is_favorite = not status.is_favorite
    status.save()
    return redirect("dashboard")

@login_required
def mark_solved(request, question_id):
    status, _ = UserQuestionStatus.objects.get_or_create(user=request.user, question_id=question_id)
    status.is_solved = True
    status.save()
    return redirect("dashboard")




