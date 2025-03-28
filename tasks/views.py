from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.dates import timezone_today

from tasks.forms import PartialTaskForm
from tasks.models import Task


class TaskListView(generic.ListView):
    model = Task
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, "task_form"):
            context["task_form"] = getattr(self, "task_form")
        else:
            context["task_form"] = PartialTaskForm(initial={
                "deadline": timezone_today()
            })

        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        if "task_form" in request.POST:
            task_form = PartialTaskForm(request.POST)

            if task_form.is_valid():
                task_form.save()
            else:
                self.task_form = task_form
                return self.get(request, *args, **kwargs)

        return redirect(reverse("task-list"))
