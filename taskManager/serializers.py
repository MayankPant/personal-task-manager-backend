from rest_framework import serializers
from .models import Task, Analytics


class TaskSerializer(serializers.ModelSerializer):
    due_date = serializers.DateTimeField(input_formats="%Y-%m-%d")
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'priority', 'status', 'created_at', 'updated_at', 'user_id']

class AnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Analytics
        fields = ['user_id', 'date', 'tasks_completed', 'tasks_created', 'high_priority_tasks', 'medium_priority_tasks', 'low_priority_tasks']

