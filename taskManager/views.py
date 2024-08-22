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
from .utils import capitalize



BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR.joinpath("dev.env"))

@api_view(['POST'])
def save_task(request: HttpRequest):
    headers, payload = request.headers, json.loads(request.body)
    print(f"Headers: {headers} \n Payload: {payload}")
    accessToken = headers.get('Authorization').split(" ")[1]
    
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
        if serializer.is_valid():
            serializer.save()
            return Response(data={"details" : "Task saved"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(data={"details" : "unsaved task"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response(status=response.status_code)

