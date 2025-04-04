from django.urls import path

from tasks.views import TaskDeleteView, TaskListView, TaskUpdateView

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("<int:pk>/update", TaskUpdateView.as_view(), name="task-update"),
    path("<int:pk>/delete", TaskDeleteView.as_view(), name="task-delete"),
]

app_name = "tasks"
