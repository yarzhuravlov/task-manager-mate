from django.test import TestCase
from django.contrib import admin

from tasks.models import TaskType, Task
from tasks.admin import TaskTypeAdmin, TaskAdmin


class TaskTypeAdminTests(TestCase):
    def test_search_fields_contains_name(self):
        admin_instance = TaskTypeAdmin(TaskType, admin.site)
        self.assertEqual(admin_instance.search_fields, ("name",))


class TaskAdminTests(TestCase):
    def setUp(self):
        self.admin = TaskAdmin(Task, admin.site)

    def test_list_display_fields(self):
        expected_fields = (
            "name",
            "task_type",
            "priority",
            "deadline",
            "is_completed",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_search_fields(self):
        expected_fields = (
            "name",
            "task_type__name",
            "assigners__username",
        )
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_list_filter_fields(self):
        expected_fields = (
            "priority",
            "is_completed",
        )
        self.assertEqual(self.admin.list_filter, expected_fields)
