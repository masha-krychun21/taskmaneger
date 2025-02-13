from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# Модель ролі (користувач, менеджер, адміністратор)
class Role(models.Model):
    name: models.CharField = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


# Модель команди
class Team(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField()
    users: models.ManyToManyField = models.ManyToManyField("CustomUser", through="UserTeam")

    def __str__(self) -> str:
        return self.name


class CustomUser(AbstractUser):
    role: Optional[models.ForeignKey[Role]] = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    teams: models.ManyToManyField = models.ManyToManyField(Team, through="UserTeam")

    def make_admin(self) -> None:
        admin_role, created = Role.objects.get_or_create(name="Administrator")
        if self.role != admin_role:
            self.role = admin_role
            self.save()

    groups: models.ManyToManyField = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",  # Уникнення конфлікту з User
        blank=True,
        related_query_name="customuser_group",
    )
    user_permissions: models.ManyToManyField = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",  # Уникнення конфлікту з User
        blank=True,
        related_query_name="customuser_permission",
    )

    def __str__(self) -> str:
        return self.username


# Між таблиця для зв'язку користувачів з командами
class UserTeam(models.Model):
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team: models.ForeignKey = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_manager: models.BooleanField = models.BooleanField(default=False)  # Якщо користувач є менеджером цієї команди

    def __str__(self) -> str:
        return f"{self.user.username} - {self.team.name}"

    def save(self, *args: Optional[tuple], **kwargs: Optional[dict]) -> None:
        # Забезпечуємо, щоб у кожній команді був тільки один менеджер
        if self.is_manager:
            UserTeam.objects.filter(team=self.team, is_manager=True).exclude(id=self.id).update(is_manager=False)
        super().save(*args, **kwargs)
