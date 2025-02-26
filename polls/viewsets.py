import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from custom_auth.models import CustomUser, Role, Team
from polls import permissions
from polls.permissions import IsAuthenticatedCustom

from .filters import TaskFilter
from .models import Comment, Notification, NotificationSettings, Task, TaskComment, TaskHistory  # TaskReminder
from .permissions import IsManagerOrAdmin
from .serializers import (
    CommentSerializer,
    CustomUserSerializer,
    NotificationSerializer,
    NotificationSettingsSerializer,
    TaskCommentSerializer,
    TaskHistorySerializer,
    # TaskReminderSerializer,
    TaskSerializer,
    TaskStatusUpdateSerializer,
    TeamSerializer,
    UserSerializer,
)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all().order_by("id")
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "deadline", "status"]
    ordering = ["created_at"]
    permission_classes = [IsAuthenticatedCustom]

    def get_queryset(self):
        user = self.request.user
        assigned_to_me = self.request.query_params.get("assigned_to_me", None)
        assigned_to_team = self.request.query_params.get("assigned_to_team", None)
        team_id = self.request.query_params.get("team_id", None)
        user_id = self.request.query_params.get("user", None)

        queryset = Task.objects.all()

        if not user.is_authenticated:
            return Task.objects.none()

        if assigned_to_me == "true":
            queryset = queryset.filter(assigned_to=user)

        if assigned_to_team == "true":
            teams = user.teams.all()
            queryset = queryset.filter(team__in=teams)

            if team_id:
                queryset = queryset.filter(team_id=team_id)

            if user_id:
                queryset = queryset.filter(assigned_to_id=user_id)

        if user.role.name == "Admin":
            if assigned_to_team == "true":
                teams = user.teams.all()
                queryset = queryset.filter(team__in=teams)

                if team_id:
                    queryset = queryset.filter(team_id=team_id)

                if user_id:
                    queryset = queryset.filter(assigned_to_id=user_id)

        return queryset

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            self.permission_classes = [IsManagerOrAdmin]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsManagerOrAdmin]
        return super().get_permissions()

    @action(detail=True, methods=["patch"])
    def status(self, request: Request, pk: int = None) -> Response:
        task = self.get_object()

        serializer = TaskStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            task.status = serializer.validated_data["status"]
            task.save(update_fields=["status"])
            return Response({"status": task.status}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(ModelViewSet):
    queryset: list[Comment] = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: list[str] = ["task", "user"]
    search_fields: list[str] = ["text"]
    ordering_fields: list[str] = ["created_at"]
    ordering: list[str] = ["created_at"]

    def get_queryset(self) -> list[Comment]:
        task_id = self.kwargs.get("task_pk")
        if task_id is None:
            raise ValidationError("task_pk is required")
        if task_id:
            return Comment.objects.filter(task_id=task_id)
        return Comment.objects.all()


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedCustom]
    filter_backends: list = [SearchFilter, OrderingFilter]
    search_fields: list[str] = ["message", "status"]
    ordering_fields: list[str] = ["created_at", "status"]
    ordering: list[str] = ["created_at"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TaskHistoryViewSet(ModelViewSet):
    queryset: list[TaskHistory] = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: list[str] = ["task", "user", "action"]
    search_fields: list[str] = ["action", "previous_value"]
    ordering_fields: list[str] = ["timestamp"]
    ordering: list[str] = ["timestamp"]


class TaskCommentViewSet(ModelViewSet):
    queryset: list[TaskComment] = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")


class UserTaskViewSet(ModelViewSet):
    queryset: list[Task] = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes: list[BasePermission] = [IsAuthenticatedCustom]

    def get_queryset(self) -> list[Task]:
        queryset: list[Task] = super().get_queryset()
        user: CustomUser = self.request.user
        return queryset.filter(assigned_to=user)


class ManagerTeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        team_id = self.kwargs["pk"]
        if team_id is None:
            raise ValidationError("pk is required")
        user = self.request.user
        return user.teams.filter(id=team_id, userteam__is_manager=True).order_by("id")


class TeamUsersViewSet(ModelViewSet):
    serializer_class = CustomUserSerializer
    ordering_fields: list[str] = ["username", "email"]
    ordering: list[str] = ["username"]

    def get_queryset(self):
        team_id = self.kwargs["team_pk"]
        if team_id is None:
            raise ValidationError("team_pk is required")
        return CustomUser.objects.filter(userteam__team_id=team_id).order_by("username")


class TeamUserTasksViewSet(ModelViewSet):
    queryset: list[Task] = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self) -> list[Task]:
        team_id = self.kwargs["team_pk"]
        user_id = self.kwargs["user_pk"]
        if team_id is None:
            raise ValidationError("team_pk is required")
        return Task.objects.filter(team__id=team_id, assigned_to__id=user_id)


class TaskStatusUpdateView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)

            if task.assigned_to != request.user:
                return Response(
                    {"error": "You do not have permission to update this task."},
                    status=HTTP_400_BAD_REQUEST,
                )

            serializer = TaskStatusUpdateSerializer(instance=task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=HTTP_400_BAD_REQUEST)


# registration
class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAdmin]

    def create(self, request, *args, **kwargs):
        manager_role_id = Role.objects.get(name="Manager").id
        admin_role_id = Role.objects.get(name="Administrator").id

        if request.user.role and request.user.role.id == manager_role_id and request.data.get("role") == admin_role_id:
            return Response({"error": "Manager cannot create administrators.."}, status=403)

        return super().create(request, *args, **kwargs)


# Notification
class NotificationSettingsViewSet(ModelViewSet):
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticatedCustom]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# class TaskReminderViewSet(ModelViewSet):
#     queryset = TaskReminder.objects.all()
#     serializer_class = TaskReminderSerializer
#     permission_classes = [permissions.IsAuthenticatedCustom]

#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)


@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.assigned_to, message=f"You have been assigned a new task: {instance.title}"
        )
    else:
        Notification.objects.create(
            user=instance.assigned_to,
            message=f"The status of your task '{instance.title}' changed to {instance.status}",
        )


logger = logging.getLogger(__name__)

# @receiver(post_save, sender=TaskReminder)
# def send_task_reminder(sender, instance, **kwargs):
#     logger.info(f"TaskReminder ID {instance.id} - remind_at: {instance.remind_at}, sent: {instance.sent}")
#     if not instance.sent and instance.remind_at <= timezone.now():
#         Notification.objects.create(user=instance.user, message=f"Reminder: Deadline for '{instance.task.title}'")
#         instance.sent = True
#         instance.save()
#         logger.info(f"Reminder sent for task {instance.task.title}")


class MarkNotificationAsRead(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.mark_as_read()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response(
                {"message": "Notification not found or doesn't belong to this user"}, status=status.HTTP_404_NOT_FOUND
            )
