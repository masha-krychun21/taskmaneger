from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Task, Comment, Notification, TaskHistory


# Inline для коментарів
class CommentInline(admin.TabularInline):
    model = Comment
    extra: int = 0
    fields: list[str] = ['user', 'text', 'created_at']
    readonly_fields: list[str] = ['created_at']
    show_change_link: bool = True
    max_num: int = 10


# Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'title', 'status', 'assigned_to', 'deadline', 'created_at')
    list_filter: tuple[str, ...] = ('status', 'assigned_to')
    search_fields: list[str] = ('title', 'description')
    inlines: list[CommentInline] = [CommentInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Task]:
        return super().get_queryset(request)


# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = ('task', 'user', 'created_at')
    list_filter: tuple[str, ...] = ('task', 'user')
    search_fields: list[str] = ('text',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Comment]:
        return super().get_queryset(request)


# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = ('message', 'status', 'created_at')
    list_filter: tuple[str, ...] = ('status',)
    search_fields: list[str] = ('message',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Notification]:
        return super().get_queryset(request)


# Task History Admin
@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = ('task', 'user', 'action', 'timestamp')
    list_filter: tuple[str, ...] = ('task', 'user', 'action')
    search_fields: list[str] = ('action', 'previous_value')

    def get_queryset(self, request: HttpRequest) -> QuerySet[TaskHistory]:
        return super().get_queryset(request)
