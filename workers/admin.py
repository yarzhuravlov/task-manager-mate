from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from workers.models import Worker, Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "position",
                    "email",
                    "is_staff",
                )
            }
        ),
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Position', {
            'fields': [
                'position',
            ],
        }),
    )

    list_display = UserAdmin.list_display + (
        "position",
    )

    list_filter = UserAdmin.list_filter + (
        "position",
    )

    search_fields = UserAdmin.search_fields + (
        "position__name",
    )
