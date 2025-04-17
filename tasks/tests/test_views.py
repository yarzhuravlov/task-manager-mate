from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from tasks.models import TaskType, Task
from workers.models import Position

User = get_user_model()
htmx_header = {"Hx-Request": True}


def create_user_and_login(test_case):
    user = User.objects.create_user(
        first_name="test_firstname",
        last_name="test_lastname",
        username="testuser",
        password="testpass",
        position=Position.get_unknown_position(),
    )
    test_case.client.login(username="testuser", password="testpass")
    return user


class TaskListViewTest(TestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_sees_task_list(self):
        create_user_and_login(self)
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(response.status_code, 200)


class TaskUpdateViewTest(TestCase):
    def setUp(self):
        self.user = create_user_and_login(self)
        self.task_type = TaskType.objects.create(name="Test Type")
        self.task = Task.objects.create(
            name="Test Task",
            task_type=self.task_type,
        )
        self.task.assigners.add(self.user)

    def test_get_update_page(self):
        response = self.client.get(
            reverse("tasks:task-update", args=[self.task.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data(self):
        response = self.client.post(
            reverse("tasks:task-update", args=[self.task.pk]),
            {
                "name": "Updated Task",
                "task_type": self.task_type.id,
                "priority": self.task.priority,
                "created_at": self.task.created_at,
                "assigners": self.task.assigners.values_list("id", flat=True),
            },
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Updated Task")
        self.assertEqual(list(self.task.assigners.all()), [self.user])
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_data(self):
        response = self.client.post(
            reverse("tasks:task-update", kwargs={"pk": self.task.pk}),
            {"name": "", "task_type": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "This field is required.",
        )
        self.assertFormError(
            response.context["form"],
            "task_type",
            "This field is required.",
        )


class TaskDeleteViewTest(TestCase):
    def setUp(self):
        self.user = create_user_and_login(self)
        self.task_type = TaskType.objects.create(name="Test Type")
        self.task = Task.objects.create(
            name="Test Task", task_type=self.task_type
        )

    def test_delete_task(self):
        response = self.client.post(
            reverse("tasks:task-delete", kwargs={"pk": self.task.pk})
        )
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        self.assertEqual(response.status_code, 302)


class TaskTypeListViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("tasks:task-type-list"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_see_list(self):
        create_user_and_login(self)
        response = self.client.get(reverse("tasks:task-type-list"))
        self.assertEqual(response.status_code, 200)


class TaskTypeDeleteViewTest(TestCase):
    def setUp(self):
        self.user = create_user_and_login(self)
        self.task_type = TaskType.objects.create(name="Type to Delete")

    def test_delete_task_type(self):
        response = self.client.post(
            reverse("tasks:task-type-delete", kwargs={"pk": self.task_type.pk})
        )
        self.assertFalse(
            TaskType.objects.filter(pk=self.task_type.pk).exists()
        )
        self.assertEqual(response.status_code, 302)


class TaskTypeCreateFormViewTest(TestCase):
    def setUp(self):
        create_user_and_login(self)

    def test_create_valid_task_type(self):
        response = self.client.post(
            reverse("tasks:task-type-create-form"),
            {"name": "New Type"},
            headers=htmx_header,
        )
        self.assertTrue(TaskType.objects.filter(name="New Type").exists())
        self.assertEqual(response.status_code, 200)

    def test_create_invalid_task_type(self):
        response = self.client.post(
            reverse("tasks:task-type-create-form"), {"name": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "name", "This field is required."
        )


class TaskTypeUpdateFormViewTest(TestCase):
    def setUp(self):
        create_user_and_login(self)
        self.task_type = TaskType.objects.create(name="Original Type")

    def test_update_valid(self):
        response = self.client.post(
            reverse("tasks:task-type-update-form", args=[self.task_type.pk]),
            {"name": "Updated Type"},
            headers=htmx_header,
        )
        self.task_type.refresh_from_db()
        self.assertEqual(self.task_type.name, "Updated Type")
        self.assertEqual(response.status_code, 200)

    def test_update_invalid(self):
        response = self.client.post(
            reverse(
                "tasks:task-type-update-form", kwargs={"pk": self.task_type.pk}
            ),
            {"name": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "name", "This field is required."
        )
