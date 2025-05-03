from django.test import TestCase
from django.contrib import admin
from workers.models import Worker, Position
from workers.admin import WorkerAdmin, PositionAdmin


class PositionAdminTests(TestCase):
    def test_search_fields(self):
        ma = PositionAdmin(Position, admin.site)
        self.assertEqual(ma.search_fields, ("name",))


class WorkerAdminTests(TestCase):
    def setUp(self):
        self.admin = WorkerAdmin(Worker, admin.site)

    def test_add_fieldsets_contains_position(self):
        found = any(
            "position" in fieldset[1]["fields"]
            for fieldset in self.admin.add_fieldsets
            if "fields" in fieldset[1]
        )
        self.assertTrue(found)

    def test_fieldsets_contains_position(self):
        found = any(
            "position" in fieldset[1]["fields"]
            for fieldset in self.admin.fieldsets
            if "fields" in fieldset[1]
        )
        self.assertTrue(found)

    def test_list_display_contains_position(self):
        self.assertIn("position", self.admin.list_display)

    def test_list_filter_contains_position(self):
        self.assertIn("position", self.admin.list_filter)

    def test_search_fields_contains_position_name(self):
        self.assertIn("position__name", self.admin.search_fields)
