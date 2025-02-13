from typing import Type

import django_filters
from django_filters.filters import CharFilter, ChoiceFilter, DateTimeFilter

from .models import Task, TaskStatus


class TaskFilter(django_filters.FilterSet):
    title: CharFilter = django_filters.CharFilter(lookup_expr="icontains", label="Заголовок")
    status: ChoiceFilter = django_filters.ChoiceFilter(choices=TaskStatus.choices, label="Статус")
    deadline: DateTimeFilter = django_filters.DateTimeFilter(lookup_expr="gte", label="Мінімальна дата")

    class Meta:
        model: Type[Task] = Task
        fields: list[str] = ["title", "status", "deadline"]
