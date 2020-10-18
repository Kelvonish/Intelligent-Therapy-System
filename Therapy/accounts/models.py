from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField( max_length=100)
    response = models.CharField( max_length=500)
    created = models.DateTimeField( auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.question

class Results(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.IntegerField()
    tag = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.tag

class Therapy(models.Model):
    tag= models.CharField( max_length=50)
    recommendation = models.TextField()

    def __str__(self):
        return self.tag
    