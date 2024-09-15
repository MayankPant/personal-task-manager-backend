from django.urls import path
from .views import save_task, analytics
urlpatterns = [
    path('task', save_task, name='save_task'),
    path('analytics', analytics, name="analytics")
]