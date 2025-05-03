from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from tasks.models import TaskType, Task
from tasks.forms import (
    TaskForm,
    PartialTaskForm,
    ChangeTaskIsCompletedForm,
    TaskSearchForm,
    TaskTypeForm,
    SearchIn,
    Status,
)
from workers.models import Position

User = get_user_model()


class TaskFormTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Development")
        self.user = User.objects.create_user(
            username="dev",
            password="123",
            first_name="Dev",
            position=Position.get_unknown_position(),
        )

    def test_valid_task_form(self):
        data = {
            "name": "Fix bug",
            "description": "Fix login bug",
            "deadline": (timezone.now() + timezone.timedelta(days=3)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "is_completed": False,
            "priority": Task.Priority.HIGH,
            "task_type": self.task_type.id,
            "assigners": [self.user.id],
        }
        form = TaskForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_task_form_missing_required(self):
        form = TaskForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("task_type", form.errors)


class PartialTaskFormTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Design")

    def test_excluded_fields(self):
        form = PartialTaskForm()
        excluded_fields = {"created_at", "is_completed", "description"}
        for field in excluded_fields:
            self.assertNotIn(field, form.fields)


class ChangeTaskIsCompletedFormTests(TestCase):
    def test_valid_checkbox_form(self):
        form_data = {"is_completed": True, "task_id": 1}
        form = ChangeTaskIsCompletedForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_task_id(self):
        form = ChangeTaskIsCompletedForm(data={"is_completed": True})
        self.assertFalse(form.is_valid())
        self.assertIn("task_id", form.errors)


class TaskSearchFormTests(TestCase):
    def test_valid_search_form(self):
        form_data = {
            "content": "feature",
            "search_in": [SearchIn.NAME, SearchIn.DESCRIPTION],
            "status": Status.ALL,
            "priority": [Task.Priority.LOW, Task.Priority.MEDIUM],
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_defaults(self):
        form = TaskSearchForm(data={})
        self.assertTrue(form.is_valid())  # All fields optional


class TaskTypeFormTests(TestCase):
    def test_valid_task_type_form(self):
        form_data = {"name": "Testing"}
        form = TaskTypeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_task_type_form(self):
        form = TaskTypeForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
