from django.db import models
# from dashboard.models import Topic
from dashboard.models import Question,Topic
# Create your models here.
class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='name',null=True,blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,related_name='topic',null=True,blank=True)
    difficulty = models.CharField(max_length=10, choices=[("Easy", "Easy"), ("Med.", "Medium"), ("Hard", "Hard")],null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    input_file = models.FileField(upload_to='testcases/inputs/')
    output_file = models.FileField(upload_to='testcases/outputs/')
    constraints=models.TextField(null=True,blank=True)
    explanations=models.TextField(null=True,blank=True)
    
    is_visible = models.BooleanField(default=True)  # True = visible on 'Run Code'

    