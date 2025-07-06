from django.shortcuts import render, redirect,get_object_or_404
from .models import Question, Topic, UserSolvedQuestion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count


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

def problem_detail(request, id):
    question = get_object_or_404(Question, id=id)
    # test_case = Topic.objects.filter(question=question).first()  # Get first test case
    
    context = {
        'question': question,
    
    }
    return render(request, 'dashboard.html', context)

# @login_required
# def toggle_favorite(request, question_id):
#     status, _ = UserQuestionStatus.objects.get_or_create(user=request.user, question_id=question_id)
#     status.is_favorite = not status.is_favorite
#     status.save()
#     return redirect("dashboard")

# @login_required
# def mark_solved(request, question_id):
#     status, _ = UserQuestionStatus.objects.get_or_create(user=request.user, question_id=question_id)
#     status.is_solved = True
#     status.save()
#     return redirect("dashboard")

@login_required
def leaderboard_view(request):
    """
    Ranks users based on the number of questions they have successfully solved.
    """
    # 1. Annotate each User object with the count of their solved questions.
    #    'usersolvedquestion' is the default related name from the ForeignKey in UserSolvedQuestion.
    #    If you set a related_name, use that instead.
    ranked_users = User.objects.annotate(
        solved_count=Count('usersolvedquestion')
    ).filter(
        solved_count__gt=0  # Only include users who have solved at least one question
    ).order_by(
        '-solved_count'  # Order by the solved count in descending order
    )

    current_user_solved_count = get_user_solved_count(request.user)

    # 2. Pass the ranked list to the template context
    context = {
        'ranked_users': ranked_users,
        'current_user_solved_count': current_user_solved_count, 
    }
    
    return render(request, 'leaderboard.html', context)



def get_user_solved_count(user):
    """
    A helper function that calculates and returns the number of questions
    a specific user has solved. Returns 0 if the user is not authenticated.
    """
    # It's crucial to handle anonymous users who don't have a profile.
    if not user.is_authenticated:
        return 0
    
    # The core logic: filter by the user and return the count.
    return UserSolvedQuestion.objects.filter(user=user).count()


# In your main app's views.py


from django.db.models import Count, Q

# Assuming 'Question' and 'Topic' are in the same app's models.py


# Import the built-in User model from Django's auth system

# ... your other views like dashboard, leaderboard_view etc. ...

@login_required
def profile_view(request, username):
    """
    Displays a user's profile with detailed stats and rank.
    """
    # Get the user object for the profile being viewed
    # Use get_object_or_404 to handle cases where the user doesn't exist
    profile_user = get_object_or_404(User, username=username)

    # --- 1. Calculate Solved Counts by Difficulty ---
    # We query the UserSolvedQuestion model, filtering by the user and the difficulty of the related question
    easy_solved_count = UserSolvedQuestion.objects.filter(user=profile_user, question__difficulty='Easy').count()
    medium_solved_count = UserSolvedQuestion.objects.filter(user=profile_user, question__difficulty='Medium').count()
    hard_solved_count = UserSolvedQuestion.objects.filter(user=profile_user, question__difficulty='Hard').count()
    total_solved = easy_solved_count + medium_solved_count + hard_solved_count

    # --- 2. Get Total Question Counts by Difficulty ---
    total_easy_questions = Question.objects.filter(difficulty='Easy').count()
    total_medium_questions = Question.objects.filter(difficulty='Medium').count()
    total_hard_questions = Question.objects.filter(difficulty='Hard').count()
    total_questions = total_easy_questions + total_medium_questions + total_hard_questions
    
    # Calculate solved percentage for the progress circle
    solved_percentage = (total_solved / total_questions * 100) if total_questions > 0 else 0

    # --- NEW: CALCULATE THE SVG CIRCLE OFFSET HERE ---
    # The circle's circumference is 2 * pi * radius (2 * 3.14159 * 42 ≈ 264)
    circumference = 264
    # Calculate the offset value that will be used in the template
    stroke_offset = circumference - (circumference * solved_percentage / 100)

    # --- 3. Calculate Leaderboard Rank ---
    # Get all users, annotated with their solve count, ordered by score
    ranked_users = User.objects.annotate(
        solved_count=Count('usersolvedquestion')
    ).order_by('-solved_count', 'date_joined') # Order by score, then join date as tie-breaker

    # Find the rank of the current profile_user
    rank = 0
    try:
        # Create a list of user IDs in their ranked order
        ranked_ids = list(ranked_users.values_list('id', flat=True))
        # Find the index of our user in that list. Index + 1 is the rank.
        rank = ranked_ids.index(profile_user.id) + 1
    except ValueError:
        # This happens if the user has 0 solves and isn't on the leaderboard
        rank = "N/A"

    # --- 4. Calculate Custom Score ---
    # Based on your formula: 1 point for Easy, 2 for Medium, 4 for Hard
    custom_score = (easy_solved_count * 1) + (medium_solved_count * 2) + (hard_solved_count * 4)

    # --- 5. Bundle everything into the context ---
    context = {
        'profile_user': profile_user,
        'easy_solved_count': easy_solved_count,
        'medium_solved_count': medium_solved_count,
        'hard_solved_count': hard_solved_count,
        'total_easy_questions': total_easy_questions,
        'total_medium_questions': total_medium_questions,
        'total_hard_questions': total_hard_questions,
        'total_solved': total_solved,
        'total_questions': total_questions,
        'solved_percentage': solved_percentage,
        'rank': rank,
        'custom_score': custom_score,
        'circumference': circumference,  # Pass the circumference
        'stroke_offset': stroke_offset,
    }

    return render(request, 'profile.html', context)

