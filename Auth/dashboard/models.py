from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=255)
    # description = models.TextField()
    # constraints = models.TextField(blank=True, null=True)
    # sample_input = models.TextField(blank=True, null=True)
    # sample_output = models.TextField(blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=[("Easy", "Easy"), ("Med.", "Medium"), ("Hard", "Hard")])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class UserQuestionStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    is_solved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')
