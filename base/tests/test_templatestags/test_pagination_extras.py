from django.test import TestCase

from django.core.paginator import Paginator
from django.template import Context

from base.templatetags.pagination_extras import register_pages_list


class RegisterPagesListTagTests(TestCase):
    def setUp(self):
        self.items = list(range(1, 11))
        self.paginator = Paginator(self.items, 1)

    def _create_context(self, page_number):
        page = self.paginator.page(page_number)
        context = Context(
            {
                "page_obj": page,
                "paginator": self.paginator,
            }
        )
        return context

    def test_middle_page(self):
        context = self._create_context(5)
        pages_count = 2

        register_pages_list(context, pages_count)

        self.assertEqual(len(context["page_list"]), 5)
        expected_pages = [3, 4, 5, 6, 7]
        self.assertEqual(
            [p.page_number for p in context["page_list"]], expected_pages
        )

        for page in context["page_list"]:
            if page.page_number == 5:
                self.assertTrue(page.active)
            else:
                self.assertFalse(page.active)

    def test_first_pages(self):
        context = self._create_context(1)
        pages_count = 2

        register_pages_list(context, pages_count)

        self.assertEqual(len(context["page_list"]), 5)
        expected_pages = [1, 2, 3, 4, 5]
        self.assertEqual(
            [p.page_number for p in context["page_list"]], expected_pages
        )

        for page in context["page_list"]:
            if page.page_number == 1:
                self.assertTrue(page.active)
            else:
                self.assertFalse(page.active)

    def test_last_pages(self):
        """Test when current page is near the end"""
        context = self._create_context(10)
        pages_count = 2

        register_pages_list(context, pages_count)

        self.assertEqual(len(context["page_list"]), 5)
        expected_pages = [6, 7, 8, 9, 10]
        self.assertEqual(
            [p.page_number for p in context["page_list"]], expected_pages
        )

        for page in context["page_list"]:
            if page.page_number == 10:
                self.assertTrue(page.active)
            else:
                self.assertFalse(page.active)

    def test_custom_page_count(self):
        context = self._create_context(5)
        pages_count = 1

        register_pages_list(context, pages_count)

        self.assertEqual(len(context["page_list"]), 3)
        expected_pages = [4, 5, 6]
        self.assertEqual(
            [p.page_number for p in context["page_list"]], expected_pages
        )

    def test_fewer_total_pages(self):
        paginator = Paginator(range(1, 4), 1)
        page = paginator.page(2)
        context = Context(
            {
                "page_obj": page,
                "paginator": paginator,
            }
        )
        pages_count = 3

        register_pages_list(context, pages_count)

        self.assertEqual(len(context["page_list"]), 3)
        expected_pages = [1, 2, 3]
        self.assertEqual(
            [p.page_number for p in context["page_list"]], expected_pages
        )

    def test_empty_return(self):
        context = self._create_context(5)
        result = register_pages_list(context, 2)
        self.assertEqual(result, "")
