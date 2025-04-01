from django.urls import path

from tasks.views import TaskListView, TaskUpdateView

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("<int:pk>/update", TaskUpdateView.as_view(), name="task-update")
]

app_name = "tasks"
