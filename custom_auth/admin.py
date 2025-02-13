from typing import Any, Optional, Union

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import CustomUser, Role, Team, UserTeam


class TeamFilter(admin.SimpleListFilter):
    title: str = "team"
    parameter_name: str = "team"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[int, str]]:
        teams: QuerySet = Team.objects.all()
        return [(team.id, team.name) for team in teams]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value():
            return queryset.filter(teams__id=self.value())
        return queryset


class UserTeamInline(admin.TabularInline):
    model: Any = UserTeam
    extra: int = 1


class CustomUserAdmin(UserAdmin):
    list_display: list[str] = ["username", "role", "is_staff", "is_active", "team_list"]
    search_fields: list[str] = ["username", "email"]
    list_filter: list[Union[str, TeamFilter]] = [
        "role",
        "is_staff",
        "is_active",
        TeamFilter,
    ]
    inlines: list[admin.TabularInline] = [UserTeamInline]

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role",)}),)

    # Можна додавати кастомні поля в `add_fieldsets` для додавання вибору ролі при створенні користувача
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)  # Додаємо поле для вибору ролі

    def team_list(self, obj: CustomUser) -> str:
        teams: QuerySet = obj.teams.all()
        if teams.exists():
            return ", ".join([team.name for team in teams])
        return "-"

    team_list.short_description: str = "Teams"


class TeamAdmin(admin.ModelAdmin):
    list_display: list[str] = ["name", "description"]
    search_fields: list[str] = ["name"]
    list_filter: list[str] = ["name"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(Team, TeamAdmin)
