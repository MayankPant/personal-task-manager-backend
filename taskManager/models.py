from django.db import models
from django.utils import timezone
import django.conf.global_settings as settings



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
    user_id = models.IntegerField()
    def __str__(self):
        return self.title

class Analytics(models.Model):
    user_id = models.IntegerField(primary_key=True)    
    date = models.DateTimeField(auto_now_add=True)
    tasks_completed = models.IntegerField(default=0)
    tasks_created = models.IntegerField(default=0)
    high_priority_tasks = models.IntegerField(default=0)
    medium_priority_tasks = models.IntegerField(default=0)
    low_priority_tasks = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Analytics'

    def __str__(self):
        return f"Analytics for {self.user_id} on {self.date}"