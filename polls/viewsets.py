from django.http import HttpRequest, HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import BasePermission
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import Task, Comment, TaskComment, Notification, TaskHistory
from .serializers import (
    CommentSerializer,
    TaskCommentSerializer,
    TaskSerializer,
    CustomUserSerializer,
    TeamSerializer,
    NotificationSerializer,
    TaskHistorySerializer,
    TaskStatusUpdateSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import TaskFilter
from custom_auth.models import CustomUser, Team
from polls.permissions import IsAuthenticatedCustom
from .permissions import IsManagerOrAdmin, IsUserOrAdminOrManager
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError



class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'status']
    ordering = ['created_at']
    permission_classes = [IsAuthenticatedCustom]  


    def get_queryset(self):
        user = self.request.user
        assigned_to_me = self.request.query_params.get('assigned_to_me', None)
        assigned_to_team = self.request.query_params.get('assigned_to_team', None)
        team_id = self.request.query_params.get('team_id', None)
        user_id = self.request.query_params.get('user', None)

        queryset = Task.objects.all()

        if assigned_to_me == 'true':  
            queryset = queryset.filter(assigned_to=user)

        if assigned_to_team == 'true':  
            teams = user.teams.all()  
            queryset = queryset.filter(team__in=teams)

            if team_id:  
                queryset = queryset.filter(team_id=team_id)

            if user_id:  
                queryset = queryset.filter(assigned_to_id=user_id)
                
        if user.role.name == 'Admin':
            if assigned_to_team == 'true':
                teams = user.teams.all()  
                queryset = queryset.filter(team__in=teams)

                if team_id:
                    queryset = queryset.filter(team_id=team_id)

                if user_id:
                    queryset = queryset.filter(assigned_to_id=user_id)

        return queryset

    def get_permissions(self) -> list[BasePermission]:
        if self.action == 'create':
            self.permission_classes = [IsManagerOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsManagerOrAdmin]
        return super().get_permissions()
    
    @action(detail=True, methods=['patch'])
    def status(self, request: Request, pk: int = None) -> Response:
        task = self.get_object()

        serializer = TaskStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            task.status = serializer.validated_data['status']
            task.save(update_fields=["status"])
            return Response({'status': task.status}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(ModelViewSet):
    queryset: list[Comment] = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: list[str] = ['task', 'user']
    search_fields: list[str] = ['text']
    ordering_fields: list[str] = ['created_at']
    ordering: list[str] = ['created_at']

    def get_queryset(self) -> list[Comment]:
        task_id: int = self.kwargs['task_pk']
        if task_id:
            return Comment.objects.filter(task_id=task_id)
        return Comment.objects.all()


class NotificationViewSet(ModelViewSet):
    queryset: list[Notification] = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends: list = [SearchFilter, OrderingFilter]
    search_fields: list[str] = ['message', 'status']
    ordering_fields: list[str] = ['created_at', 'status']
    ordering: list[str] = ['created_at']


class TaskHistoryViewSet(ModelViewSet):
    queryset: list[TaskHistory] = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: list[str] = ['task', 'user', 'action']
    search_fields: list[str] = ['action', 'previous_value']
    ordering_fields: list[str] = ['timestamp']
    ordering: list[str] = ['timestamp']


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
        team_id = self.kwargs['pk']  
        user = self.request.user
        return user.teams.filter(id=team_id, userteam__is_manager=True).order_by('id')



class TeamUsersViewSet(ModelViewSet):
    # queryset: list[CustomUser] = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    ordering_fields: list[str] = ['username', 'email']  
    ordering: list[str] = ['username']  
    
    def get_queryset(self):
        team_id = self.kwargs['team_pk']  
        return CustomUser.objects.filter(userteam__team_id=team_id).order_by('username')



class TeamUserTasksViewSet(ModelViewSet):
    queryset: list[Task] = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self) -> list[Task]:
        team_id = self.kwargs['team_pk']
        user_id = self.kwargs['user_pk']
        return Task.objects.filter(team__id=team_id, assigned_to__id=user_id)


class TaskStatusUpdateView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)

            if task.assigned_to != request.user:
                return Response({"error": "You do not have permission to update this task."}, status=HTTP_400_BAD_REQUEST)

            serializer = TaskStatusUpdateSerializer(instance=task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=HTTP_400_BAD_REQUEST)