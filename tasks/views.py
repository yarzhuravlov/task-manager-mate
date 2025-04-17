from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic import UpdateView, CreateView
from django.views.generic.dates import timezone_today

from base.utils.core import getattr_or_default
from tasks.forms import (
    PartialTaskForm,
    ChangeTaskIsCompletedForm,
    TaskForm,
    TaskSearchForm,
    SearchIn,
    Status,
    TaskTypeForm,
)
from tasks.models import Task, TaskType

User = get_user_model()


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
            task_form = getattr(self, "task_form")
            context["open_task_modal"] = True
        else:
            task_form = PartialTaskForm(initial={"deadline": timezone_today()})
            context["open_task_modal"] = False
        context["task_form"] = self._render_task_form_html(task_form)

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

        context["workers"] = User.objects.all()

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

            queryset = TaskListView._update_queryset_with_content(
                queryset,
                search_form,
            )

            queryset = TaskListView._update_queryset_with_status(
                queryset,
                search_form,
            )

            queryset = TaskListView._update_queryset_with_priority(
                queryset, search_form
            )

        return queryset

    @staticmethod
    def _update_queryset_with_content(
        queryset: QuerySet[Task],
        search_form: TaskSearchForm,
    ):
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

        return queryset

    @staticmethod
    def _update_queryset_with_status(
        queryset: QuerySet[Task],
        search_form: TaskSearchForm,
    ):
        if status := search_form.cleaned_data.get("status"):
            match status:
                case Status.COMPLETE.value:
                    queryset = queryset.filter(is_completed=True)
                case Status.INCOMPLETE.value:
                    queryset = queryset.filter(is_completed=False)
                case _:
                    pass

        return queryset

    @staticmethod
    def _update_queryset_with_priority(
        queryset: QuerySet[Task], search_form: TaskSearchForm
    ):
        if priority := search_form.cleaned_data.get("priority"):
            queryset = queryset.filter(priority__in=priority)

        return queryset

    def _render_task_form_html(self, task_form: TaskForm):
        task_form_html = render_to_string(
            "includes/base_form.html",
            {
                "form": task_form,
                "form_submit_value": "Add",
                "form_submit_name": "task_form",
            },
            request=self.request,
        )
        return task_form_html


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = TaskForm
    model = Task

    def get_success_url(self):
        return reverse_lazy("tasks:task-update", args=(self.kwargs["pk"],))


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:task-list")


def get_task_type_form_context(
    task_type_form: TaskTypeForm,
    form_submit_name,
):
    if task_type_form.instance and task_type_form.instance.id:
        form_submit_value = "Update"
        hx_target = "#updateTaskTypeModalBody"
        hx_post = reverse(
            "tasks:task-type-update-form",
            args=[task_type_form.instance.id],
        )
    else:
        form_submit_value = "Add"
        hx_target = "#createTaskTypeModalBody"
        hx_post = reverse("tasks:task-type-create-form")

    return {
        "form": task_type_form,
        "form_submit_value": form_submit_value,
        "form_submit_name": form_submit_name,
        "hx_post": hx_post,
        "hx_target": hx_target,
        "hx_swap": "outerHtml",
    }


def render_task_type_form_html(
    task_type_form: TaskTypeForm,
    request: HttpRequest,
    form_submit_name,
):
    return render_to_string(
        "partials/base_htmx_form.html",
        get_task_type_form_context(task_type_form, form_submit_name),
        request=request,
    )


class TaskTypeCreateFormView(LoginRequiredMixin, CreateView):
    template_name = "partials/base_htmx_form.html"
    model = TaskType
    form_class = TaskTypeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            get_task_type_form_context(
                TaskTypeForm(),
                "task_type_form",
            )
        )

        return context

    def form_valid(self, form):
        form.instance.save()
        if "Hx-Request" in self.request.headers:
            return render(
                request=self.request,
                template_name="partials/task_type.html",
                context={
                    "task_type": form.instance,
                    "hx_swap_obb_tbody": "afterbegin:#task-types-table-body",  # noqa: E501
                },
            )

    def form_invalid(self, form):
        return HttpResponse(
            render_task_type_form_html(
                form,
                self.request,
                "task_type_form",
            ),
        )


class TaskTypeUpdateFormView(
    LoginRequiredMixin,
    UpdateView,
):
    model = TaskType
    context_object_name = "task_type"
    template_name = "partials/base_htmx_form.html"
    form_class = TaskTypeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            get_task_type_form_context(
                context["form"], "task_type_update_form"
            )
        )

        return context

    def form_valid(self, form):
        if "Hx-Request" in self.request.headers:
            form.instance.save()
            return render(
                request=self.request,
                template_name="partials/task_type.html",
                context={
                    "task_type": form.instance,
                    "hx_swap_obb_tr": f"outerHTML:#taskType{form.instance.id}",
                },
            )

    def form_invalid(self, form):
        return HttpResponse(
            render_task_type_form_html(
                form,
                self.request,
                "task_type_form",
            ),
        )


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    template_name = "tasks/task_type_list.html"
    context_object_name = "task_types"

    def get_queryset(self):
        return TaskType.objects.prefetch_related("tasks")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("tasks:task-type-list")
