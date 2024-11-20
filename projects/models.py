from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User)
    startdate = models.DateTimeField(auto_now_add=True)
    enddate = models.DateTimeField(null=True)
    createdby = models.IntegerField(null=False)

    def __str__(self):
        return self.name

class Task(models.Model):
    name  = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)
    startdate = models.DateTimeField(auto_now_add=True)
    enddate = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
    
class Notes(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
