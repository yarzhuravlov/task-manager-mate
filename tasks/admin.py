from django.contrib import admin

from tasks.models import TaskType, Task


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_type",
        "priority",
        "deadline",
        "is_completed",
    )

    search_fields = (
        "name",
        "task_type__name",
        "assigners__username",
    )

    list_filter = (
        "priority",
        "is_completed"
    )
