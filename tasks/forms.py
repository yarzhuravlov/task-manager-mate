from django import forms
from django.contrib.auth import get_user_model

from tasks.models import Task

Worker = get_user_model()


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            attrs={'type': 'datetime-local'},
        )
    )
    assigners = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.select_related("position"),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple()
    )

    class Meta:
        model = Task
        fields = "__all__"


class PartialTaskForm(TaskForm):
    class Meta(TaskForm.Meta):
        exclude = ("created_at", "is_completed", "description")
