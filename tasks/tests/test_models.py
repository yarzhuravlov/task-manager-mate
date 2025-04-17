from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from tasks.models import TaskType, Task
from workers.models import Position

User = get_user_model()


class TaskTypeModelTests(TestCase):
    def test_str_returns_name(self):
        task_type = TaskType.objects.create(name="Development")
        self.assertEqual(str(task_type), "Development")

    def test_ordering_by_name(self):
        t1 = TaskType.objects.create(name="Zeta")
        t2 = TaskType.objects.create(name="Alpha")
        t3 = TaskType.objects.create(name="Beta")
        task_types = list(TaskType.objects.all())
        self.assertEqual(task_types, [t2, t3, t1])


class TaskModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.position = Position.get_unknown_position()

    def setUp(self):
        self.task_type = TaskType.objects.create(name="Testing")
        self.user = User.objects.create_user(
            username="john",
            password="pass1234",
            position=self.position,
        )

    def test_str_representation(self):
        task = Task.objects.create(
            name="Write unit tests",
            task_type=self.task_type,
            deadline=timezone.now(),
        )
        self.assertEqual(str(task), f"Write unit tests ({self.task_type})")

    def test_defaults(self):
        task = Task.objects.create(
            name="Default Check",
            task_type=self.task_type,
        )
        self.assertFalse(task.is_completed)
        self.assertEqual(task.priority, Task.Priority.LOW)
        self.assertEqual(task.description, "")
        self.assertIsNotNone(task.created_at)

    def test_many_to_many_assigners(self):
        task = Task.objects.create(
            name="Assign users",
            task_type=self.task_type,
        )
        task.assigners.add(self.user)
        self.assertIn(self.user, task.assigners.all())

    def test_ordering(self):
        now = timezone.now()
        t1 = Task.objects.create(
            name="Task 1",
            task_type=self.task_type,
            deadline=None,
            priority=Task.Priority.HIGH,
        )
        t2 = Task.objects.create(
            name="Task 2",
            task_type=self.task_type,
            deadline=now,
            priority=Task.Priority.MEDIUM,
        )
        t3 = Task.objects.create(
            name="Task 3",
            task_type=self.task_type,
            deadline=now,
            priority=Task.Priority.URGENT,
            is_completed=True,
        )

        tasks = list(Task.objects.all())
        self.assertEqual(tasks, [t2, t1, t3])
