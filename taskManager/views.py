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

@api_view(['POST'])
def save_task(request: HttpRequest):
    headers, payload = request.headers, json.loads(request.body)
    print(f"Headers: {headers} \n Payload: {payload}")
    
    print(headers.get("Authorization"))
    response = requests.post('http://127.0.0.1:8000/api/auth/user', headers={"Authorization": headers.get("Authorization")})
    print(f"Response from Auth: {response.text}")
    if response.status_code == 200:
        response = json.loads(response.text)
        user_id = response['user'].get('id')
        # get task data
        title = payload["title"]
        print(title)
        description = payload["description"]
        print(description)
        due_date = payload["dueDate"]
        print(due_date)
        date_format = "%Y-%m-%d"
        due_date = datetime.strptime(due_date, date_format)
        print(f"Converted date: {type(due_date)}  {due_date}")
        task_status = capitalize(payload['status'])
        print(task_status)
        priority = capitalize(payload['priority'])
        print(priority)
        # add user id to payload
        payload['user_id'] = user_id
        
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "status": task_status,
            "user_id": user_id
        }
        print(payload)
        serializer = TaskSerializer(data=payload)
        
        
        #updating the anaylytics for this uer
        print("Type and date of task creation", type(datetime.today().strftime('%Y-%m-%d')), datetime.today().strftime('%Y-%m-%d'))
        analytics = {
            "user_id":user_id,
            "tasks_created":1,
            "high_priority_tasks": 1 if priority == "High" else 0,
            "medium_priority_tasks": 1 if priority == "Medium" else 0,
            "low_priority_tasks": 1 if priority == "Low" else 0,
        }
        print(f"Analytics: {analytics}")
        analytics_serializer =AnalyticsSerializer(data=analytics)
        
        
        
        if serializer.is_valid() and analytics_serializer.is_valid():
            serializer.save()
            analytics_serializer.save()
            return Response(data={"details" : "Task saved"}, status=status.HTTP_202_ACCEPTED)
        else:
            print(analytics_serializer.error_messages)
            return Response(data={"details" : "unsaved task"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    elif response.status_code == 401:
        """
        If the access token expires, we send a response ton client
        to generate a new access token using the refresh token
        """
        return Response(data={"details" : "unsaved task"}, status=status.HTTP_401_UNAUTHORIZED)

            

@api_view(['GET'])
def analytics(request: HttpRequest):
    headers = request.headers
    print(f"Headers: {headers}")
    
    print(headers.get("Authorization"))
    response = requests.post('http://127.0.0.1:8000/api/auth/user', headers={"Authorization": headers.get("Authorization")})
    print(f"Response from Auth: {response.text}")
    if response.status_code == 200:
        response = json.loads(response.text)
        user_id = response['user'].get('id')
        user_analytics = Analytics.objects.filter(user_id=user_id)
        user_tasks = Task.objects.filter(user_id=user_id)
        print(f"User data: {user_tasks} \n {user_analytics}")
        user_data = parse_user_data(user_tasks, 3)
        return Response(data=user_data, status=status.HTTP_207_MULTI_STATUS)
    elif response.status_code == 401:
        """
        If the access token expires, we send a response ton client
        to generate a new access token using the refresh token
        """
        return Response(data={"details" : "unsaved task"}, status=status.HTTP_401_UNAUTHORIZED)
