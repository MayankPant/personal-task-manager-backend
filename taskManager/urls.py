from django.urls import path, re_path
from .views import save_task, analytics
urlpatterns = [
    path('task', save_task, name='save_task'),
    re_path(r'^analytics/-?(\d*)/?$', analytics, name="analytics")
]