from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .viewsets import (
    CommentViewSet,
    ManagerTeamViewSet,
    MarkNotificationAsRead,
    NotificationSettingsViewSet,
    NotificationViewSet,
    TaskHistoryViewSet,
    TaskReminderViewSet,
    TaskStatusUpdateView,
    TaskViewSet,
    TeamUsersViewSet,
    TeamUserTasksViewSet,
    UserViewSet,
)

# Основний роутер
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"task-history", TaskHistoryViewSet, basename="taskhistory")
router.register(r"manager/teams", ManagerTeamViewSet, basename="manager-teams")
router.register(r"teams", ManagerTeamViewSet, basename="team")
router.register(r"users", UserViewSet)
router.register(r"notification-settings", NotificationSettingsViewSet, basename="notification-settings")
router.register(r"task-reminders", TaskReminderViewSet, basename="task-reminder")

tasks_router = NestedDefaultRouter(router, r"tasks", lookup="task")
tasks_router.register(r"comments", CommentViewSet, basename="task-comments")

teams_router = NestedDefaultRouter(router, r"teams", lookup="team")
teams_router.register(r"users", TeamUsersViewSet, basename="team-users")

team_user_tasks_router = NestedDefaultRouter(teams_router, r"users", lookup="user")
team_user_tasks_router.register(r"tasks", TeamUserTasksViewSet, basename="team-user-tasks")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(tasks_router.urls)),
    path("", include(teams_router.urls)),
    path("", include(team_user_tasks_router.urls)),
    path(
        "tasks/<int:pk>/status/",
        TaskStatusUpdateView.as_view(),
        name="task-update-status",
    ),
    path("notifications/<int:notification_id>/mark_as_read/", MarkNotificationAsRead.as_view(), name="mark_as_read"),
]
