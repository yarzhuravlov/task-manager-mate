from django.test import TestCase
from django.contrib.auth import get_user_model
from workers.models import Position

Worker = get_user_model()


class PositionModelTests(TestCase):

    def test_str_returns_name(self):
        position = Position.objects.create(name="Manager")
        self.assertEqual(str(position), "Manager")

    def test_get_unknown_position_creates_and_returns_unknown(self):
        unknown = Position.get_unknown_position()
        self.assertEqual(unknown.name, "Unknown")

        again = Position.get_unknown_position()
        self.assertEqual(Position.objects.filter(name="Unknown").count(), 1)
        self.assertEqual(unknown, again)


class WorkerModelTests(TestCase):

    def setUp(self):
        self.position = Position.objects.create(name="Developer")

    def test_worker_str_representation(self):
        worker = Worker.objects.create_user(
            username="jdoe",
            password="pass1234",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )
        expected_str = "John Doe (Developer)"
        self.assertEqual(str(worker), expected_str)

    def test_worker_verbose_names(self):
        self.assertEqual(Worker._meta.verbose_name, "worker")
        self.assertEqual(Worker._meta.verbose_name_plural, "workers")
