from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from tasks.models import Task, TaskType

User = get_user_model()


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            attrs={"type": "datetime-local"},
        )
    )
    assigners = forms.ModelMultipleChoiceField(
        queryset=User.objects.select_related(
            "position",
        ).exclude(
            first_name="",
        ),
        required=False,
        widget=forms.widgets.SelectMultiple(
            attrs={
                "class": "selectpicker form-control",
                "data-live-search": "true",
                "multiple": True,
                "data-style": "form-select bootstrap-select-in-crispy",
            }
        ),
    )

    class Meta:
        model = Task
        fields = "__all__"


class PartialTaskForm(TaskForm):
    class Meta(TaskForm.Meta):
        exclude = ("created_at", "is_completed", "description")


class ChangeTaskIsCompletedForm(forms.Form):
    is_completed = forms.BooleanField(
        label="",
        required=False,
        widget=forms.CheckboxInput(attrs={"submit": True}),
    )
    task_id = forms.IntegerField(widget=forms.HiddenInput())


class SearchIn(models.TextChoices):
    NAME = "name"
    DESCRIPTION = "description"
    ASSIGNERS = "assigners"


class Status(models.TextChoices):
    ALL = "all"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class TaskSearchForm(forms.Form):
    content = forms.CharField(required=False)
    search_in = forms.MultipleChoiceField(
        choices=SearchIn.choices,
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple,
    )
    status = forms.ChoiceField(
        choices=Status.choices,
        required=False,
    )
    priority = forms.MultipleChoiceField(
        choices=Task.Priority.choices,
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple,
    )


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = ("name",)


class TaskTypeUpdateForm(forms.ModelForm):
    id = forms.IntegerField(
        widget=forms.widgets.HiddenInput()
    )

    class Meta:
        model = TaskType
        fields = "__all__"
