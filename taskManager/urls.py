from django.urls import path
from .views import save_task
urlpatterns = [
    path('task', save_task, name='save_task'),
]