from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.utils import timezone
import django.conf.global_settings as settings

# the user tabe wont be managed by taskManager migrations but will allow its reference

User = get_user_model()

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    tasks_completed = models.IntegerField(default=0)
    tasks_created = models.IntegerField(default=0)
    high_priority_tasks = models.IntegerField(default=0)
    medium_priority_tasks = models.IntegerField(default=0)
    low_priority_tasks = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']
        verbose_name_plural = 'Analytics'

    def __str__(self):
        return f"Analytics for {self.user.username} on {self.date}"