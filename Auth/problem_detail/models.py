from django.db import models
from dashboard.models import Topic
# Create your models here.
class Detail(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    description = models.TextField()
    constraints = models.TextField(blank=True, null=True)
    sample_input = models.TextField(blank=True, null=True)
    sample_output = models.TextField(blank=True, null=True)
    Explanation=models.TextField(blank=True, null=True)

