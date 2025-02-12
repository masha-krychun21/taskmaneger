from rest_framework import serializers
from .models import Task, Comment, Notification, TaskHistory, TaskStatus
from rest_framework.exceptions import ValidationError
from polls.models import TaskComment
from custom_auth.models import CustomUser, Team, Role


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = '__all__'


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = '__all__'


# Серіалізатор для користувачів
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'teams']


# Серіалізатор для команд
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


# Серіалізатор для ролей
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']



class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=TaskStatus.choices, required=True)

    class Meta:
        model = Task
        fields = ['status']

