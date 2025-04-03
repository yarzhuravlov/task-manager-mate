from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.dates import timezone_today

from base.utils import getattr_or_default
from tasks.forms import (
    PartialTaskForm,
    ChangeTaskIsCompletedForm,
    TaskForm,
    TaskSearchForm,
    SearchIn,
    Status,
)
from tasks.models import Task


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 7
    search_form_class = TaskSearchForm

    def setup(self, request, *args, **kwargs):
        search_form = self.search_form_class(request.GET)

        if search_form.is_valid() and any(search_form.cleaned_data.values()):
            self.search_form = search_form

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Task.objects.all()
        queryset = self._update_queryset_with_search_form(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, "task_form"):
            context["task_form"] = getattr(self, "task_form")
        else:
            context["task_form"] = PartialTaskForm(
                initial={"deadline": timezone_today()}
            )

        for task in context["task_list"]:
            task.is_completed_form = ChangeTaskIsCompletedForm(
                initial={"task_id": task.id, "is_completed": task.is_completed}
            )

        context["search_form"] = getattr_or_default(
            self,
            "search_form",
            self.search_form_class(
                initial={"search_in": [SearchIn.NAME], "status": [Status.ALL]}
            ),
        )

        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        if "task_form" in request.POST:
            task_form = PartialTaskForm(request.POST)

            if task_form.is_valid():
                task_form.save()
            else:
                self.task_form = task_form
                return self.get(request, *args, **kwargs)

        if "is_completed_form" in request.POST:
            Task.objects.filter(pk=int(request.POST["task_id"])).update(
                is_completed=(request.POST.get("is_completed") == "on")
            )

        return redirect(request.get_full_path())

    def _update_queryset_with_search_form(
        self,
        queryset: QuerySet[Task],
    ) -> QuerySet[Task]:
        if search_form := getattr_or_default(self, "search_form"):
            if content := search_form.cleaned_data.get("content"):
                search_in = search_form.cleaned_data["search_in"]

                search_in_query = Q()

                if SearchIn.NAME in search_in:
                    search_in_query |= Q(name__icontains=content)
                if SearchIn.DESCRIPTION in search_in:
                    search_in_query |= Q(description__icontains=content)
                if SearchIn.ASSIGNERS in search_in:
                    search_in_query |= (
                        Q(assigners__username__icontains=content)
                        | Q(assigners__first_name__icontains=content)
                        | Q(assigners__last_name__icontains=content)
                    )

                queryset = queryset.filter(search_in_query)

            if status := search_form.cleaned_data.get("status"):
                match status:
                    case Status.COMPLETE.value:
                        queryset = queryset.filter(is_completed=True)
                    case Status.INCOMPLETE.value:
                        queryset = queryset.filter(is_completed=False)
                    case _:
                        pass

            if priority := search_form.cleaned_data.get("priority"):
                queryset = queryset.filter(priority__in=priority)

        return queryset


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = TaskForm
    model = Task

    def get_success_url(self):
        return reverse_lazy("tasks:task-update", args=(self.kwargs["pk"],))
