from django.urls import path, re_path
from .views import save_task, analytics, delete_task
urlpatterns = [
    path('task', save_task, name='save_task'),
    path('task/<int:task_id>', delete_task, name="delete_task"),
    re_path(r'^analytics/-?(\d*)/?$', analytics, name="analytics")
]