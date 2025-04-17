from django.urls import path

from tasks.views import (
    TaskDeleteView,
    TaskListView,
    TaskUpdateView,
    TaskTypeListView,
    TaskTypeDeleteView,
    TaskTypeCreateFormView, TaskTypeUpdateFormView,
)

urlpatterns = [
    path(
        "",
        TaskListView.as_view(),
        name="task-list",
    ),
    path(
        "<int:pk>/update",
        TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "<int:pk>/delete",
        TaskDeleteView.as_view(),
        name="task-delete",
    ),
    path(
        "tasks-types/",
        TaskTypeListView.as_view(),
        name="task-type-list",
    ),
    path(
        "tasks-types/<int:pk>/delete/",
        TaskTypeDeleteView.as_view(),
        name="task-type-delete",
    ),
    path(
        "tasks-types/forms/create/",
        TaskTypeCreateFormView.as_view(),
        name="task-type-create-form",
    ),
    path(
        "tasks-types/forms/<int:pk>/update/",
        TaskTypeUpdateFormView.as_view(),
        name="task-type-update-form",
    ),
]

app_name = "tasks"
