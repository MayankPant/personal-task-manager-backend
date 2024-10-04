from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer, AnalyticsSerializer
from .models import Task, Analytics
from rest_framework import status
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
import requests
import os
from pathlib import Path
import dotenv
import json
from datetime import datetime
from .utils import capitalize, parse_user_data



BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR.joinpath("dev.env"))

@api_view(['POST', 'PUT'])
def save_task(request):
    headers, payload = request.headers, json.loads(request.body)
    print(f"Headers: {headers} \n Payload: {payload}")

    auth_response = requests.post('http://127.0.0.1:8000/api/auth/user', headers={"Authorization": headers.get("Authorization")})
    print(f"Response from Auth: {auth_response.text}")
    
    if auth_response.status_code == 200:
        auth_data = json.loads(auth_response.text)
        user_id = auth_data['user'].get('id')

        # Extract task data from payload
        title = payload["title"]
        description = payload["description"]
        due_date = payload["dueDate"]
        date_format = "%Y-%m-%d"
        due_date = datetime.strptime(due_date, date_format)
        task_status = capitalize(payload['status'])
        priority = capitalize(payload['priority']['value'])

        # Update payload with additional user info
        payload['user_id'] = user_id

        # Update case: Check if it's a PUT request and if task exists
        if request.method == 'PUT':
            # Assume 'id' is passed in the payload for the task to be updated
            task_id = payload.get('task_id')
            if not task_id:
                return Response({"detail": "Task ID is required for updating"}, status=status.HTTP_400_BAD_REQUEST)

            task = get_object_or_404(Task, id=task_id, user_id=user_id)  # Ensure the task belongs to the user
            serializer = TaskSerializer(task, data={
                "task_id": task_id,
                "title": title,
                "description": description,
                "due_date": due_date,
                "priority": priority,
                "status": task_status,
                "user_id" : user_id
            })
            user_analytics = Analytics.objects.get(user_id=user_id)
            analytics = {
                "user_id": user_id,
                "tasks_created": user_analytics.tasks_created,  # Only increment for new task
                "tasks_completed": user_analytics.tasks_completed if task_status == "Completed" else user_analytics.tasks_completed - 1,
                "high_priority_tasks": user_analytics.high_priority_tasks + 1 if priority == "High" else user_analytics.high_priority_tasks - 1,
                "medium_priority_tasks": user_analytics.medium_priority_tasks + 1 if priority == "Medium" else user_analytics.medium_priority_tasks - 1,
                "low_priority_tasks": user_analytics.low_priority_tasks + 1 if priority == "Low" else user_analytics.low_priority_tasks - 1,
            }
            analytics_serializer = AnalyticsSerializer(user_analytics, data=analytics)

            if serializer.is_valid() and analytics_serializer.is_valid():
                serializer.save()
                analytics_serializer.save()
                operation = "updated"
                return Response({"detail": f"Task {operation} successfully"}, status=status.HTTP_202_ACCEPTED)
                
        else:
            # Create case: POST request
            serializer = TaskSerializer(data={
                "title": title,
                "description": description,
                "due_date": due_date,
                "priority": priority,
                "status": task_status,
                "user_id": user_id
            })
            operation = "created"

        # Analytics data
            user_analytics = Analytics.objects.get(user_id=user_id)
            analytics = {
                "user_id": user_id,
                "tasks_completed": user_analytics.tasks_completed + 1 if task_status == "Completed" else user_analytics.tasks_completed,
                "tasks_created": user_analytics.tasks_created + 1 if request.method == 'POST' else user_analytics.tasks_created,  # Only increment for new tasks
                "high_priority_tasks": user_analytics.high_priority_tasks + 1 if priority == "High" else user_analytics.high_priority_tasks,
                "medium_priority_tasks": user_analytics.medium_priority_tasks + 1 if priority == "Medium" else user_analytics.medium_priority_tasks,
                "low_priority_tasks": user_analytics.low_priority_tasks + 1 if priority == "Low" else user_analytics.low_priority_tasks,
            }
            analytics_serializer = AnalyticsSerializer(user_analytics, data=analytics)

            if serializer.is_valid() and analytics_serializer.is_valid():
                serializer.save()
                analytics_serializer.save()
                return Response({"detail": f"Task {operation} successfully"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif auth_response.status_code == 401:
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['DELETE'])
def delete_task(request: HttpRequest, task_id):
    headers = request.headers
    print(f"Headers: {headers} \n\n\n\n")
    print(headers.get("Authorization"))
    response = requests.post('http://127.0.0.1:8000/api/auth/user', headers={"Authorization": headers.get("Authorization")})
    print(f"Response from Auth: {response.text}")
    if response.status_code == 200:
        response = json.loads(response.text)
        user_id = response['user'].get('id')
        task = get_object_or_404(Task, id=task_id, user_id=user_id)  # Ensure the task belongs to the user
        user_analytics = get_object_or_404(Analytics, user_id=user_id)
        print(f"User analytics: {user_analytics}")
        analytics = {
            "user_id": user_id,
            "tasks_completed": user_analytics.tasks_completed - 1 if task.status == 'Completed' else user_analytics.tasks_completed,  # Only increment for new tasks
            "tasks_created": user_analytics.tasks_created,
            "high_priority_tasks": user_analytics.high_priority_tasks - 1 if task.priority == "High" else user_analytics.high_priority_tasks,
            "medium_priority_tasks": user_analytics.medium_priority_tasks - 1 if task.priority == "Medium" else user_analytics.medium_priority_tasks,
            "low_priority_tasks": user_analytics.low_priority_tasks - 1 if task.priority == "Low" else user_analytics.low_priority_tasks,
        }
        analytics_serializer = AnalyticsSerializer(user_analytics, data=analytics)
        
        if analytics_serializer.is_valid():
            """
            Task object is needed to update analytics and hence it cant be deleted first
            """
            analytics_serializer.save()
            task.delete()
            operation="deleted"
            return Response({"detail": f"Task {operation} successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(analytics_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif response.status_code == 401:
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
def analytics(request: HttpRequest, rows):
    headers = request.headers
    print(f"Headers: {headers}")
    if rows is not None:
        try:
            rows = int(rows)
            # Now you can safely use 'rows' as an integer
            
        except ValueError:
            rows=-1

    
    print(headers.get("Authorization"))
    response = requests.post('http://127.0.0.1:8000/api/auth/user', headers={"Authorization": headers.get("Authorization")})
    print(f"Response from Auth: {response.text}")
    if response.status_code == 200:
        response = json.loads(response.text)
        user_id = response['user'].get('id')
        user_analytics = Analytics.objects.filter(user_id=user_id)
        user_tasks = Task.objects.filter(user_id=user_id)
        print(f"User data: {user_tasks} \n {user_analytics}")
        user_data = parse_user_data(user_tasks, rows)
        return Response(data=user_data, status=status.HTTP_207_MULTI_STATUS)
    elif response.status_code == 401:
        """
        If the access token expires, we send a response ton client
        to generate a new access token using the refresh token
        """
        return Response(data={"details" : "unsaved task"}, status=status.HTTP_401_UNAUTHORIZED)
